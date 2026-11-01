using Test
using Random
using Statistics

include(joinpath(@__DIR__, "..", "gestational_window_simulation.jl"))

@testset "gestational window simulation" begin
    @test shifted_exposure(30.0, 28.0, 32.0, 0.0) == 30.0
    @test shifted_exposure(30.0, 28.0, 32.0, 7.0) == 32.0
    @test shifted_exposure(30.0, 28.0, 32.0, -7.0) == 28.0
    @test shifted_exposure(30.0, 28.0, 32.0, 100.0) == 32.0
    @test shifted_exposure(30.0, 28.0, 32.0, -100.0) == 28.0

    @test tofloat("1.5") == 1.5
    @test isnan(tofloat("not-a-number"))
    @test isnan(tofloat(missing))
    @test toint("2") == 2
    @test toint(missing) === nothing
    @test tobool("TRUE")
    @test tobool("1")
    @test !tobool("0")
    @test !tobool(missing)

    @test sigma_for("semagestac") == 3.5
    @test sigma_for("gestacao_categoria") == 7.0
    @test sigma_for("missing") == 7.0

    Random.seed!(20261101)
    n = 400
    x = randn(n) .* 5.0 .+ 30.0
    year = rand(2010.0:2025.0, n)
    age = rand(18.0:42.0, n)
    male = rand(0.0:1.0, n)
    eta = 0.35 .* (x .- mean(x)) .+ 0.01 .* (year .- mean(year)) .- 0.02 .* (age .- mean(age)) .+ 0.1 .* male
    y = [rand() < 1.0 / (1.0 + exp(-e)) ? 1.0 : 0.0 for e in eta]
    fit = fit_logistic(y, x, year, age, male)
    @test fit !== nothing
    @test fit.n == n
    @test fit.events == Int(sum(y))
    @test isfinite(fit.or)
    @test fit.lo < fit.hi
    @test fit.or > 1.0

    constant = fill(30.0, n)
    @test fit_logistic(y, constant, year, age, male) === nothing
end
