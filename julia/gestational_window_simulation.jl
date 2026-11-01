# Julia module: Monte Carlo measurement-error simulation for the gestational window
#
# Goal
# ----
# The main analysis assigns an area-level Tmax to a cardiac organogenesis window
# estimated from gestational age.  Gestational age is measured with error and the
# conception date is not observed.  This module propagates that uncertainty by
# sampling a conception-window shift for each birth and refitting the same
# birth-level logistic model.
#
# The three exposure columns (main, -7 days, +7 days) are used as anchors.  For a
# sampled shift delta in [-7, +7] days, exposure is linearly interpolated:
#   delta >= 0: x = x_main + (delta/7) * (x_late - x_main)
#   delta <  0: x = x_main + (delta/7) * (x_main - x_early)
#
# This is a measurement-error sensitivity simulation, not a full Bayesian
# hierarchical model.  It is intentionally kept in Julia as a well-delimited
# numerical module; the rest of the pipeline remains Python/R.
#
# Usage
# -----
#   julia --project=julia julia/gestational_window_simulation.jl
#   JULIA_REPS=200 julia --project=julia julia/gestational_window_simulation.jl
#
# Input (local, not redistributed): data_processed/sinasc_campos_with_exposure.csv
# Outputs: outputs/tables/julia_gestational_window_simulation.csv
#          reports/julia_gestational_window_simulation.json

using CSV
using JSON
using Dates
using LinearAlgebra
using Random
using Statistics

const ROOT = normpath(joinpath(@__DIR__, ".."))
const INPUT = joinpath(ROOT, "data_processed", "sinasc_campos_with_exposure.csv")
const OUT_CSV = joinpath(ROOT, "outputs", "tables", "julia_gestational_window_simulation.csv")
const OUT_JSON = joinpath(ROOT, "reports", "julia_gestational_window_simulation.json")
const REPS = parse(Int, get(ENV, "JULIA_REPS", "500"))
const SEED = 20261101
const DELTA_MIN = -7.0
const DELTA_MAX = 7.0

function tofloat(x)::Float64
    ismissing(x) && return NaN
    s = strip(string(x))
    isempty(s) && return NaN
    try
        return parse(Float64, s)
    catch
        return NaN
    end
end

function toint(x)::Union{Int,Nothing}
    f = tofloat(x)
    isnan(f) && return nothing
    return round(Int, f)
end

function tobool(x)::Bool
    ismissing(x) && return false
    s = lowercase(strip(string(x)))
    return s in ("true", "1", "1.0", "yes")
end

function shifted_exposure(main::Float64, early::Float64, late::Float64, delta::Float64)::Float64
    d = clamp(delta, DELTA_MIN, DELTA_MAX)
    if d >= 0
        return main + (d / 7.0) * (late - main)
    else
        return main + (d / 7.0) * (main - early)
    end
end

function sigma_for(source::String)::Float64
    # SEMAGESTAC is a measured week; the categorical midpoint is coarser.
    return source == "semagestac" ? 3.5 : 7.0
end

function fit_logistic(
    y::Vector{Float64},
    x::Vector{Float64},
    year::Vector{Float64},
    age::Vector{Float64},
    male::Vector{Float64},
)
    n = length(y)
    sx = std(x)
    (n < 20 || sx == 0 || std(year) == 0 || std(age) == 0) && return nothing
    X = hcat(
        ones(n),
        (x .- mean(x)) ./ sx,
        year .- mean(year),
        age .- mean(age),
        male,
    )
    beta = zeros(Float64, 5)
    converged = false
    for _ in 1:40
        eta = X * beta
        p = 1.0 ./ (1.0 .+ exp.(-eta))
        w = max.(p .* (1.0 .- p), 1e-9)
        z = eta .+ (y .- p) ./ w
        Xw = X .* sqrt.(w)
        try
            beta_new = (Xw' * Xw) \ (Xw' * (sqrt.(w) .* z))
            if norm(beta_new - beta) < 1e-9
                beta = beta_new
                converged = true
                break
            end
            beta = beta_new
        catch
            return nothing
        end
    end
    converged || return nothing
    eta = X * beta
    p = 1.0 ./ (1.0 .+ exp.(-eta))
    w = max.(p .* (1.0 .- p), 1e-9)
    cov = try
        inv(X' * (X .* w))
    catch
        return nothing
    end
    se = sqrt(max(cov[2, 2], 0.0))
    or = exp(beta[2])
    lo = exp(beta[2] - 1.96 * se)
    hi = exp(beta[2] + 1.96 * se)
    return (or=or, lo=lo, hi=hi, beta=beta[2], se=se, n=n, events=Int(sum(y)))
end

function load_data()
    isfile(INPUT) || error("Input not found: $INPUT. This file is local and not redistributed.")
    file = CSV.File(
        INPUT;
        select=[
            :is_chd,
            :sexo,
            :idademae,
            :year,
            :gestation_source,
            :win_temperature_2m_max_mean,
            :win_temperature_2m_max_mean_early,
            :win_temperature_2m_max_mean_late,
        ],
    )
    y = Float64[]
    main = Float64[]
    early = Float64[]
    late = Float64[]
    year = Float64[]
    age = Float64[]
    male = Float64[]
    source = String[]
    for row in file
        xm = tofloat(row.win_temperature_2m_max_mean)
        xe = tofloat(row.win_temperature_2m_max_mean_early)
        xl = tofloat(row.win_temperature_2m_max_mean_late)
        (isnan(xm) || isnan(xe) || isnan(xl)) && continue
        sex = toint(row.sexo)
        sex === nothing && continue
        sex in (1, 2) || continue
        a = tofloat(row.idademae)
        yr = tofloat(row.year)
        (isnan(a) || isnan(yr)) && continue
        push!(y, tobool(row.is_chd) ? 1.0 : 0.0)
        push!(main, xm)
        push!(early, xe)
        push!(late, xl)
        push!(year, yr)
        push!(age, a)
        push!(male, sex == 1 ? 1.0 : 0.0)
        push!(source, ismissing(row.gestation_source) ? "missing" : string(row.gestation_source))
    end
    return (; y, main, early, late, year, age, male, source)
end

function main()
    data = load_data()
    n = length(data.y)
    events = Int(sum(data.y))
    n > 0 || error("No complete observations after filtering")
    println("Julia gestational-window simulation: n=$n events=$events reps=$REPS")

    rows = NamedTuple[]
    fixed = [(-7.0, "fixed_minus_7d"), (-3.5, "fixed_minus_3.5d"), (0.0, "fixed_main"),
             (3.5, "fixed_plus_3.5d"), (7.0, "fixed_plus_7d")]
    fixed_results = Dict{String,Any}()
    for (delta, label) in fixed
        x = shifted_exposure.(data.main, data.early, data.late, delta)
        fit = fit_logistic(data.y, x, data.year, data.age, data.male)
        fit === nothing && continue
        push!(rows, (scenario=label, replicate=0, n=fit.n, events=fit.events,
                     or_per_sd=round(fit.or; digits=4), ci_low=round(fit.lo; digits=4),
                     ci_high=round(fit.hi; digits=4), ci_excludes_null=(fit.lo > 1.0 || fit.hi < 1.0)))
        fixed_results[label] = Dict("delta_days" => delta, "or_per_sd" => fit.or,
                                    "ci_low" => fit.lo, "ci_high" => fit.hi, "n" => fit.n,
                                    "events" => fit.events)
    end

    rng = MersenneTwister(SEED)
    mc_or = Float64[]
    mc_lo = Float64[]
    mc_hi = Float64[]
    for rep in 1:REPS
        x = Vector{Float64}(undef, n)
        for i in 1:n
            sigma = sigma_for(data.source[i])
            delta = clamp(sigma * randn(rng), DELTA_MIN, DELTA_MAX)
            x[i] = shifted_exposure(data.main[i], data.early[i], data.late[i], delta)
        end
        fit = fit_logistic(data.y, x, data.year, data.age, data.male)
        fit === nothing && continue
        push!(mc_or, fit.or)
        push!(mc_lo, fit.lo)
        push!(mc_hi, fit.hi)
        push!(rows, (scenario="monte_carlo", replicate=rep, n=fit.n, events=fit.events,
                     or_per_sd=round(fit.or; digits=4), ci_low=round(fit.lo; digits=4),
                     ci_high=round(fit.hi; digits=4), ci_excludes_null=(fit.lo > 1.0 || fit.hi < 1.0)))
    end

    summary = Dict(
        "n_replicates" => length(mc_or),
        "or_mean" => isempty(mc_or) ? nothing : mean(mc_or),
        "or_median" => isempty(mc_or) ? nothing : median(mc_or),
        "or_q025" => isempty(mc_or) ? nothing : quantile(mc_or, 0.025),
        "or_q975" => isempty(mc_or) ? nothing : quantile(mc_or, 0.975),
        "proportion_or_gt_1" => isempty(mc_or) ? nothing : mean(mc_or .> 1.0),
        "proportion_ci_excludes_null" => isempty(mc_lo) ? nothing : mean((mc_lo .> 1.0) .| (mc_hi .< 1.0)),
    )

    mkpath(dirname(OUT_CSV))
    mkpath(dirname(OUT_JSON))
    CSV.write(OUT_CSV, rows)
    report = Dict(
        "module" => "gestational-window Monte Carlo measurement-error simulation",
        "language" => "Julia",
        "julia_version" => string(VERSION),
        "generated_at" => string(Dates.now(UTC)),
        "input" => "data_processed/sinasc_campos_with_exposure.csv",
        "n" => n,
        "events" => events,
        "replicates_requested" => REPS,
        "seed" => SEED,
        "sigma_days" => Dict("semagestac" => 3.5, "gestacao_categoria" => 7.0, "missing" => 7.0),
        "delta_range_days" => [DELTA_MIN, DELTA_MAX],
        "fixed_scenarios" => fixed_results,
        "monte_carlo" => summary,
        "note" => "Monte Carlo measurement-error sensitivity, not a full Bayesian hierarchical model. Exposure is interpolated between the main, -7-day and +7-day windows. Outputs contain only aggregate estimates.",
        "output_csv" => "outputs/tables/julia_gestational_window_simulation.csv",
    )
    open(OUT_JSON, "w") do io
        JSON.print(io, report, 2)
    end
    println("fixed main OR: ", get(get(fixed_results, "fixed_main", Dict()), "or_per_sd", NaN))
    println("Monte Carlo OR median: ", summary["or_median"], "  95% interval: ", summary["or_q025"], "–", summary["or_q975"])
    println("written: ", OUT_CSV)
    println("written: ", OUT_JSON)
end

if abspath(PROGRAM_FILE) == @__FILE__
    main()
end
