I'm looking to take the grouped output from the time series split function as demonstrated in time_series_modelling.ipynb and create a linear model across all groups by refactoring the pyparsnip_core and pyparsnip_timeseries library to support this use case. 

plan:

Before we start building this out, I want to do some planning with you. I first want you to make a project plan for this. Inside projectplan.md please build an in-depth plan for the task. Have high-level checkpoints for each major step and feature, then in each checkpoint have a broken down list of small tasks you'll need to do to complete that checkpoint. Also in this plan include instructions we will give to a researcher agent that will research user needs and a feature planning agent that will plan the roadmap for us. We will then review this plan together.

execute:

Feel free to start working on these checkpoints now, let's review and test the library after each full checkpoint.

Feel free to start working on these checkpoints    │
│   now, let's review and test the library after each  │
│   full checkpoint. Run the python scripts and        │
│   notebooks after each checkpoint to make sure       │
│   everything works end to end and fix any issues.    │
│   Code according to the guidelines in @claude.md

In the @reference/ folder, there is an R ecosystem called tidymodels that provides a unified modeling and ML framework. I want to convert these libraries into a single Python package while preserving as much functionality as possible. Specifically, I want to unify the functionality from @reference/modeltime-master/ with @reference/parsnip-main/ since I'll primarily use this library for time series statistical and machine learning modeling at scale. The unified interface should support:

1. Fitting a single model on ungrouped data
2. Fitting multiple models to each group of a grouped dataset
3. Supporting global and panel models where the model is estimated and fit across multiple groups simultaneously

I want the outputs of any fit model to be the @/model_outputs_csvs three datasets here - model_outputs, coefficients and stats as dataframes. All outputs should be in recordset format so multiple models can be stacked into these datasets without changing the schema or column layout of these datasets. For models without coefficients, return details of the hyperparameters.

As a simple example implement linear regression from scikit learn and statsmodels as separate engines of linear model.
Other models to consider would be:
1. Random Forest
2. Gradient boosting
3. XGBoost
4. Prophet
5. LASSO regression
6. Ridge regression
7. naive time series models/benchmarks
8. MARs
9. ARIMA/SARIMAX
10. LightGBM
11. Catboost

For time series models also consider
1. recursive models/forecasting

With time series regressions all models in the model registry should return predictions indexed by date. 

Core Infrastructure:
        Model registry system
        ModelSpec and ModelFit classes
        Engine abstraction layer
Basic Model Types:
        Linear regression (Ridge) with sklearn
        Logistic regression with sklearn (L1, L2, Elastic Net)
        ARIMA time series with statsmodels
Key Features
        Formula interface with patsy
        Prediction interfaces
        Output DataFrames (the main request)

Before we start building this out, I want to do some planning with you. I first want you to make a project plan for this. Inside projectplan.md please build an in-depth plan for the task. Have high-level checkpoints for each major step and feature, then in each checkpoint have a broken down list of small tasks you'll need to do to complete that checkpoint. Also in this plan include instructions we will give to a researcher agent that will research user needs and a feature planning agent that will plan the roadmap for us. We will then review this plan together.
