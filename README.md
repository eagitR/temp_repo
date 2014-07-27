# Analysing the "mtcars" data base 
========================================================

The "mtcars" data base is analysed for investigating: (1) the effect of automatic or manual transmission on MPG, and (2) quantifying the MPG difference between automatic and manual transmissions. For this purpose the best parsimonious model is found based on the eliminating the least significant variables from the model and choosing a model with highest adjusted R^2.The role of different factors including the "am" factor (automatic/manual) on the MPG of the vehichles is studied. The observations and reasonings are supported by figures and tables. 

## Fitting a Multi-variable Linear Regression Model

The effect of different factorson the performance of the cars (MPG) is studied by fitting a multivariable linear regression model to the data. Starting from a complete model, the best parsimonious model is found by identifying the most significant variables on the MPG and the model with highest adjusted R^2. At the first step the "drat" parameter with highest P-value (0.9876) is distinguished as the least important parameter and eliminated, which has resulted in increase in the adjusted R^2 value and P-values of the remaining parameters of the model (the scattered plot for MPG versus this parameter can be found in the appendix). In the next step parameters "gear" and "carb" are identified as factors with small effect on MPG and deleted from the model resulting in the increase in the mentioned criteria. Finally, the best model first order linear model is found as the linear combination of "cyl", "hp", "wt", "vs", and "am" parameters with R^2 = 0.8418, F-Statistics = 28.49 (6 and 25 DF), and 5.064e-10 P-value. The coefficients of the chosen parameters and the residual plots for this model are as shown below.      

```{r, echo=FALSE, fig.width=7,fig.height=6}
model_t<-lm(mpg~.-drat-gear-carb-disp-qsec,mtcars)
summary(model_t)

par(mfrow=c(2,2)); plot(model_t)
```
##### Figure 1. Residuals plots

It can be obsrved that the residuals are distributed almost normally, but since the sample size is small, justifying other effects such as homoescedacity can not be done easily. The model suggests that the manual transmission can considerably decrease the fuel consumption. Taking the intercept equal to zero for the mentioned model, the coefficient of the "am" factor (automatic/manual) will be 2.70384, which suggest that on average the manual transmision will result in 2.70384 more MPG. There are meaningful relations between variables. For example cars with more cylanders are supposed to have higher horse power and recognizing these relationships can help to simplifying the model.

The pairwise relationships of the variables are shown by Figure 2 in the appendix. It can be observed that the parameters "disp", "hp", and "cyl" are highly correlated and increase in each of them can result in highe values for the others. Therefore, between the remaining parameters "hp" and "cyl" one can be eliminated withput significant decrease in model's ability on representing the data. If the factor "cyl" be eliminated from the model, the p_value of the parameters will significantly increase in exchange to slight change in the R^2 value. Further simplifying the model by eliminating the least remaining important parmater "vs" will result in the following model:

``` {r, echo=FALSE}
model_t<-lm(mpg~.-drat-gear-carb-disp-qsec-cyl-vs,mtcars)
summary(model_t)
```

If only the P-value criteria is chosen for selecting the parmaters of the model, based on P-values and 5% significance level parameter "am" can be neglected, and the new model will be consist of all signifcant parameters with slightly         less R^2 value:

``` {r, echo=FALSE}
model_t<-lm(mpg~.-drat-gear-carb-disp-qsec-cyl-vs-am,mtcars)
summary(model_t)
```

This study shows that on average the manual transmission will result in higher millage and less fuel consumption, but the type of transmission is not the only factor that is dominating the changes in "mpg" variable. It can be distinguished form the Figure 2 that the higher "am" (manual transmission) means less "wt" and higher "disp", whcich suggests that the reason that manual transmission has resulted in higher MPG could be that the lighter and smaller cars have this type of transmission. 


## Appendix


```{r fig.width=7, fig.height=6}
pairs(mtcars)
```
##### Figure 2. Model variables' paired plot 
