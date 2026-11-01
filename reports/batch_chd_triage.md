# Triagem da fila de curadoria em lote

Gerado: 2026-11-01

Esta triagem **não altera evidências**. Ela apenas prioriza a leitura humana
dos registros que a regra estrita não promoveu. A classe é heurística e o
motivo está na coluna `triage_reason` do CSV.

| Classe | Registros | O que significa |
|---|---:|---|
| human_numeric | 97 | estudo humano com tamanho de efeito explícito |
| human_qualitative | 0 | estudo humano com associação descrita sem número |
| human_no_effect | 0 | estudo humano sem linguagem de associação no resumo |
| human_unconfirmed | 172 | estudo humano; exposição ou fenótipo candidato não confirmado no resumo |
| synthesis | 17 | revisão ou meta-análise |
| experimental | 165 | estudo animal ou celular |
| clinical | 60 | estudo cirúrgico, diagnóstico ou de dispositivo |
| unclassified | 93 | sem sinal suficiente para classificar |
| no_abstract | 1 | resumo indisponível no PubMed |
| reviewed | 8 | já possui decisão de revisão |

## human_numeric (97)

| PMID | Título | Exposições candidatas | Fenótipos candidatos |
|---|---|---|---|
| 10230836 | Maternal risk factors and major associated defects in infants with Down syndrome. | EXP:ALCOHOL;EXP:SMOKE | CHD:TOF;CHD:VSD |
| 10555617 | Maternal smoking and congenital heart defects. | EXP:SMOKE | CHD:PDA |
| 11517521 | [Long-term results of valve-retaining homograft and xenograft patch for transannular reconstruction of the right ventric | EXP:ALCOHOL | CHD:TOF |
| 12797457 | Population-based study of l-transposition of the great arteries: possible associations with environmental factors. | EXP:SMOKE | CHD:TGA |
| 1399016 | Occupational risk factors for congenital heart disease. | EXP:PEST;EXP:SMOKE;EXP:SOLV | CHD:VSD |
| 1415327 | Can maternal risk factors influence the presence of major birth defects in infants with Down syndrome? | EXP:ALCOHOL;EXP:SMOKE | CHD:AVSD;CHD:VSD |
| 14991912 | Maternal lifestyle factors and risk for ventricular septal defects. | EXP:ALCOHOL;EXP:SMOKE | CHD:VSD |
| 1572431 | Risk factors for conal malformations of the heart. | EXP:ALCOHOL;EXP:PEST;EXP:SMOKE | CHD:TOF;CHD:TRUNCUS |
| 1574882 | Clues in diagnosing congenital heart disease. | EXP:ALCOHOL | CHD:COA |
| 16391975 | A cluster of hypoplastic left heart malformation in Baltimore, Maryland. | EXP:DIOXIN;EXP:SOLV | CHD:AS;CHD:COA;CHD:HLHS |
| 18188637 | Cardiac malformations are increased in infants of mothers with epilepsy. | EXP:VPA | CHD:ASD;CHD:PDA;CHD:PS;CHD:TOF;CHD:VSD |
| 18377476 | Congenital heart defects and fetal alcohol spectrum disorders. | EXP:ALCOHOL | CHD:ASD;CHD:VSD |
| 18381510 | Maternal smoking and congenital heart defects. | EXP:ALCOHOL;EXP:SMOKE | CHD:AVSD |
| 18456715 | Double outlet right ventricle: aetiologies and associations. | EXP:ALCOHOL;EXP:VPA | CHD:DORV |
| 1882350 | Maternal exposure to chemical and physical factors during pregnancy and cardiovascular malformations in the offspring. | EXP:ALCOHOL;EXP:PEST;EXP:SMOKE;EXP:SOLV | CHD:VSD |
| 1893664 | [Effects of antiepileptic drugs on delivery and early childhood--comparison among mono-therapies of valproic acid, pheny | EXP:VPA | CHD:VSD |
| 19135190 | Maternal exposure to ambient air pollutants and risk of congenital anomalies. | EXP:PM10;EXP:SMOKE | CHD:PDA |
| 19258486 | Ambient air pollution and cardiovascular malformations in Atlanta, Georgia, 1986-2003. | EXP:CO;EXP:NO2;EXP:O3;EXP:PM10 | CHD:ASD;CHD:COA;CHD:HLHS;CHD:PDA;CHD:PS;CHD:TOF;CHD:VSD |
| 19358286 | Urban versus rural residence and occurrence of septal heart defects in Texas. | EXP:PEST | CHD:ASD;CHD:VSD |
| 19819865 | Ambient air pollution and risk of congenital anomalies in England, 1991-1999. | EXP:METALS;EXP:NO2;EXP:PM10 | CHD:TOF |
| 2068244 | Risk factors for ventricular septal defect in Finland. | EXP:ALCOHOL;EXP:SMOKE;EXP:SOLV | CHD:VSD |
| 21291342 | Severe fetal valproate syndrome: combination of complex cardiac defect, multicystic dysplastic kidney, and trigonocephal | EXP:VPA | CHD:ASD;CHD:COA;CHD:EBSTEIN |
| 21329916 | Ambient air pollution and congenital heart disease: a register-based study. | EXP:CO;EXP:NO2;EXP:O3;EXP:PM10 | CHD:PS;CHD:TOF;CHD:VSD |
| 21397265 | Myocardial expression of heat shock protein 70i protects early postoperative right ventricular function in cyanotic tetr | EXP:HEAT | CHD:TOF |
| 21591246 | Maternal alcohol drinking pattern during pregnancy and the risk for an offspring with an isolated congenital heart defec | EXP:ALCOHOL | CHD:ASD;CHD:VSD |
| 21987466 | Lack of maternal folic acid supplementation is associated with heart defects in Down syndrome: a report from the Nationa | EXP:ALCOHOL;EXP:SMOKE | CHD:AVSD |
| 22645896 | [Parental smoking during early pregnancy and congenital heart defects]. | EXP:SMOKE | CHD:COA;CHD:PS |
| 23832875 | Complex cardiac defects after ethanol exposure during discrete cardiogenic events in zebrafish: prevention with folic ac | EXP:ALCOHOL;EXP:METALS | CHD:AVSD |
| 24135485 | Valproic acid silencing of ascl1b/Ascl1 results in the failure of serotonergic differentiation in a zebrafish model of f | EXP:VPA | CHD:ASD |
| 24185815 | Prenatal unilateral cerebellar hypoplasia in a series of 26 cases: significance and implications for prenatal diagnosis. | EXP:ALCOHOL | CHD:COA |
| 24727555 | Maternal exposure to criteria air pollutants and congenital heart defects in offspring: results from the national birth  | EXP:ALCOHOL;EXP:CO;EXP:NO2;EXP:O3;EXP:PM10;EXP:PM25;EXP:SMOKE | CHD:COA;CHD:HLHS;CHD:PS |
| 24916166 | Arsenic in drinking water and congenital heart anomalies in Hungary. | EXP:METALS | CHD:ASD |
| 24920293 | First-trimester exposure to bupropion and risk of cardiac malformations. | EXP:SMOKE | CHD:VSD |
| 25002319 | Durability of large diameter right ventricular outflow tract conduits in adults with congenital heart disease. | EXP:SMOKE | CHD:TOF;CHD:TRUNCUS |
| 2525370 | [Extracardiac malformations in tetralogy of Fallot]. | EXP:ALCOHOL | CHD:TOF;CHD:VSD |
| 25262086 | Residential agricultural pesticide exposures and risk of selected congenital heart defects among offspring in the San Jo | EXP:PEST | CHD:COA;CHD:HLHS;CHD:PS;CHD:TOF |
| 2583071 | Congenital anomalies associated with maternal exposure to oxydemeton-methyl. | EXP:PEST | CHD:PDA |
| 26118863 | Maternal periconceptional alcohol consumption and congenital heart defects. | EXP:ALCOHOL;EXP:METALS | CHD:TOF |
| 26196779 | Associations between exposure to ambient benzene and PM(2.5) during pregnancy and the risk of selected birth defects in  | EXP:PM10;EXP:PM25 | CHD:COA;CHD:TAPVC;CHD:TRUNCUS |
| 26554783 | Air Pollution and the Risk of Cardiac Defects: A Population-Based Case-Control Study. | EXP:CO;EXP:NO2;EXP:O3;EXP:PM10 | CHD:ASD;CHD:PDA;CHD:VSD |
| 26853919 | Bayesian multinomial probit modeling of daily windows of susceptibility for maternal PM2.5 exposure and congenital heart | EXP:PM10;EXP:PM25 | CHD:PS;CHD:TOF |
| 26883477 | Maternal exposure to air pollutant PM2.5 and PM10 during pregnancy and risk of congenital heart defects. | EXP:PM10;EXP:PM25 | CHD:VSD |
| 26987204 | [Study on congenital cardiac anomalies induced by arsenic exposure before and during maternal pregnancy in fetal rats]. | EXP:METALS | CHD:ASD;CHD:TOF;CHD:VSD |
| 27752048 | Ozone and Other Air Pollutants and the Risk of Congenital Heart Defects. | EXP:CO;EXP:NO2;EXP:O3 | CHD:TOF;CHD:VSD |
| 2787814 | Risk factors for conotruncal cardiac defects in Atlanta. | EXP:ALCOHOL;EXP:SMOKE | CHD:TOF;CHD:TRUNCUS |
| 28373593 | Maternal Antihypertensive Medication Use and Congenital Heart Defects: Updated Results From the National Birth Defects P | EXP:SMOKE | CHD:ASD;CHD:COA;CHD:PS;CHD:VSD |
| 28557713 | Effects of Prenatal PM10 Exposure on Fetal Cardiovascular Malformations in Fuzhou, China: A Retrospective Case-Control S | EXP:PM10 | CHD:ASD;CHD:PDA;CHD:TOF;CHD:VSD |
| 28988253 | Prevalence of congenital heart diseases in children with Down syndrome in Mansoura, Egypt: a retrospective descriptive s | EXP:SMOKE | CHD:ASD;CHD:AVSD;CHD:VSD |
| 29544375 | Obstetric and perinatal outcomes in pregnancies with isolated foetal congenital heart abnormalities. | EXP:ALCOHOL;EXP:SMOKE | CHD:TGA |
| 29859881 | Is post exposure prevention of teratogenic damage possible: Studies on diabetes, valproic acid, alcohol and anti folates | EXP:ALCOHOL;EXP:CO;EXP:VPA | CHD:ASD |
| 30571202 | Projected Future Cancer Risks in Children Treated With Fluoroscopy-Guided Cardiac Catheterization Procedures. | EXP:METALS;EXP:SMOKE | CHD:ASD;CHD:PDA |
| 30696385 | Projected Changes in Maternal Heat Exposure During Early Pregnancy and the Associated Congenital Heart Defect Burden in  | EXP:HEAT | CHD:ASD |
| 30766556 | GATA4 molecular screening and assessment of environmental risk factors in a Moroccan cohort with tetralogy of Fallot. | EXP:SMOKE | CHD:TOF |
| 30819207 | Prenatal arsenic exposure alters the placental expression of multiple epigenetic regulators in a sex-dependent manner. | EXP:METALS | CHD:PDA |
| 30861318 | Midterm outcomes of right ventricular outflow tract reconstruction using the Freestyle xenograft. | EXP:METALS | CHD:TOF |
| 31272016 | Spatial variations in ambient ultrafine particle concentrations and risk of congenital heart defects. | EXP:CO;EXP:NO2;EXP:O3;EXP:PM10;EXP:PM25 | CHD:ASD;CHD:VSD |
| 31555342 | Ambient air pollution and congenital heart defects in Lanzhou, China. | EXP:NO2;EXP:PM10;EXP:SMOKE | CHD:PDA |
| 3181012 | [Congenital alcoholic cardiomyopathy in 3 children]. | EXP:ALCOHOL | CHD:TOF;CHD:VSD |
| 31991146 | 5-aminolevulinic acid inhibits oxidative stress and ameliorates autistic-like behaviors in prenatal valproic acid-expose | EXP:VPA | CHD:ASD |
| 32335433 | Maternal occupational exposure to polycyclic aromatic hydrocarbons and the risk of isolated congenital heart defects amo | EXP:SMOKE | CHD:TOF |
| 33135766 | Maternal occupational exposure and congenital heart defects in offspring. | EXP:METALS;EXP:PEST;EXP:SOLV | CHD:AS;CHD:COA;CHD:PS;CHD:VSD |
| 33250054 | Contemporary epidemiology of rising atrial septal defect trends across USA 1991-2016: a combined ecological geospatiotem | EXP:ALCOHOL;EXP:SMOKE | CHD:ASD |
| 33569925 | Gene-environment interactions between air pollution and biotransformation enzymes and risk of birth defects. | EXP:CO;EXP:NO2;EXP:PM10;EXP:PM25 | CHD:TGA;CHD:TOF |
| 34097890 | Association between maternal exposure to gaseous pollutants and atrial septal defect in China: A nationwide population-b | EXP:CO;EXP:NO2;EXP:O3;EXP:PM10;EXP:PM25 | CHD:ASD |
| 34361990 | Seasonality of Hypoplastic Left Heart Syndrome and Single Ventricle Heart in Poland in the Context of Air Pollution. | EXP:PM10 | CHD:HLHS |
| 34476711 | Associations between ambient heat exposure early in pregnancy and risk of congenital heart defects: a large population-b | EXP:HEAT | CHD:ASD;CHD:PDA |
| 34508749 | Maternal Smoking and Congenital Heart Defects, National Birth Defects Prevention Study, 1997-2011. | EXP:SMOKE | CHD:DORV |
| 34892371 | Effect of Valproic Acid on Maternal - Fetal Heart Rates and Coupling in Mice on Embryonic day 15.5 (E15.5). | EXP:VPA | CHD:ASD |
| 34920182 | Maternal exposure to air pollution and congenital heart diseases in Henan, China: A register-based case-control study. | EXP:CO;EXP:NO2;EXP:O3;EXP:PM10;EXP:PM25 | CHD:ASD;CHD:TOF |
| 35014860 | Association of Alcohol Use Diagnostic Codes in Pregnancy and Offspring Conotruncal and Endocardial Cushion Heart Defects | EXP:ALCOHOL | CHD:AVSD |
| 35521669 | Maternal nicotine exposure induces congenital heart defects in the offspring of mice. | EXP:SMOKE | CHD:DORV |
| 35991008 | Relationship between maternal exposure to heavy metal titanium and offspring congenital heart defects in Lanzhou, China: | EXP:METALS | CHD:PDA |
| 36341763 | Prepregnancy exposure to dietary arsenic and congenital heart defects. | EXP:METALS | CHD:DORV;CHD:TGA;CHD:VSD |
| 36369789 | Influenza vaccination during pregnancy and risk of selected major structural congenital heart defects, National Birth De | EXP:ALCOHOL;EXP:SMOKE | CHD:HLHS;CHD:TAPVC |
| 37551363 | Parental risk factors associated with congenital heart disease in a Thai population: multivariable analysis. | EXP:SMOKE | CHD:TOF;CHD:VSD |
| 38394684 | Epidemiology studies on effects of lithium salts in pregnancy are confounded by the inability to control for other poten | EXP:ALCOHOL;EXP:SMOKE | CHD:EBSTEIN |
| 39108168 | Racial disparities in maternal exposure to ambient air pollution during pregnancy and prevalence of congenital heart def | EXP:CO;EXP:O3;EXP:PM10;EXP:PM25 | CHD:AVSD;CHD:TOF |
| 39217202 | Maternal exposure to ambient ozone and fetal congenital heart defects: a national multicenter study in China. | EXP:NO2;EXP:O3;EXP:PM25 | CHD:PS;CHD:TGA;CHD:TOF;CHD:VSD |
| 40248504 | Biodegradable polymeric occluder with controllable locking structure for closure of atrial septal defect via interventio | EXP:METALS | CHD:ASD |
| 40269475 | Using Residual Newborn Blood Spots to Investigate CpG Methylation in Relation to Air Pollution and Congenital Heart Defe | EXP:O3;EXP:PM10 | CHD:TOF |
| 4038218 | Truncus arteriosus and facial dysmorphism. | EXP:ALCOHOL | CHD:TRUNCUS |
| 40680714 | Maternal exposure to ambient air pollution and risk of congenital heart defects in offspring: A population-based cohort  | EXP:CO;EXP:NO2;EXP:O3;EXP:PM10;EXP:PM25 | CHD:TOF;CHD:VSD |
| 40803438 | Joint effects of PM2.5 components during periconception on offspring congenital heart disease risk in Chongqing, China. | EXP:CO;EXP:PM10;EXP:PM25 | CHD:PDA |
| 40812671 | Triple-phase VPA administration in Sprague-Dawley rats: A cost-effective ASD model unveiling the synaptic-mitochondrial- | EXP:VPA | CHD:ASD |
| 40910975 | Right Ventricular Outflow Tract Stenting in a Premature Infant With Tetralogy of Fallot. | EXP:METALS | CHD:PS;CHD:TOF |
| 40994230 | Covered stents for implantation into the right ventricular outflow tract in infants with tetralogy of Fallot/pulmonary a | EXP:METALS | CHD:TOF;CHD:VSD |
| 42110157 | DNA Methylation and Fetal Programming of Cardiovascular Disease: From Congenital Heart Diseases to Adult Cardiovascular  | EXP:ALCOHOL;EXP:SMOKE | CHD:COA;CHD:TOF |
| 42776135 | Long Non-Coding Ribonucleic Acid Taurine Up-Regulated Gene 1 Accelerates Ventricular Septal Defect Formation in Children | EXP:VPA | CHD:VSD |
| 6512489 | Investigation of a temporal cluster of left sided congenital heart disease. | EXP:ALCOHOL;EXP:SMOKE | CHD:COA;CHD:HLHS |
| 6543069 | [Combination of ventricular septal defect with unilateral pulmonary artery stenoses and contralateral pulmonary hyperten | EXP:ALCOHOL | CHD:VSD |
| 7195990 | Intrinsic defects in the fetal alcohol syndrome: studies on 76 cases from British Columbia and the Yukon Territory. | EXP:ALCOHOL | CHD:TOF;CHD:VSD |
| 7394725 | Maternal hormone therapy and congenital heart disease. | EXP:ALCOHOL;EXP:SMOKE | CHD:HLHS |
| 7801298 | Risk factors for hypoplastic left heart syndrome. | EXP:ALCOHOL;EXP:PEST;EXP:SMOKE | CHD:HLHS |
| 8211818 | Sodium valproate-induced cardiovascular abnormalities in the Jcl:ICR mouse fetus: peak sensitivity of gestational day an | EXP:VPA | CHD:AVSD;CHD:DORV;CHD:HLHS;CHD:VSD |
| 8367829 | Risk factors for coarctation of the aorta. | EXP:ALCOHOL;EXP:SMOKE | CHD:COA |
| 8949354 | [Embryofetopathy due to valproate: a pathology only little known. Apropos of 4 cases]. | EXP:VPA | CHD:TOF |
| 9737553 | Attributable fraction for cardiac malformations. | EXP:PEST;EXP:SOLV | CHD:ASD;CHD:AVSD;CHD:COA;CHD:HLHS;CHD:TOF;CHD:VSD |
