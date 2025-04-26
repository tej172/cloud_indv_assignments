# Chapter 3: Training Constants

Welcome back! In the [previous chapter](02_tuning_hyperparameter_space.md), we explored the **Tuning Hyperparameter Space**, which defines the range of possibilities for settings we want to experiment with, like searching for the best oven temperature or sugar amount in our recipe.

But what about the parts of the recipe that *don't* change? Like using a standard-sized measuring cup (e.g., always 1 cup) or a default oven preheat temperature if the recipe doesn't specify otherwise? In machine learning, we also have fixed values that we use consistently during the training process. These are our **Training Constants**.

## The Problem: Keeping Standard Settings Consistent

Imagine you and your teammates are all working on training the same machine learning model. You're trying different approaches (different hyperparameters, like we saw in Chapter 2). But some basic settings should probably stay the same for everyone, at least initially, to ensure fair comparisons or provide a reliable baseline.

For example:
*   How many data samples (sentences) should the model look at in one go (the "batch size")?
*   If we use a standard learning algorithm (an "optimizer" like Adam or SGD) without tuning its learning speed, what default speed should we use?

If everyone picks a different batch size or a different default learning speed, it becomes hard to compare results or even understand what's going on. We need a way to define and use these standard, fixed values easily and consistently.

## What are Training Constants?

**Training Constants** are fixed numerical values defined in our project that are used during the model training process. They are *not* typically changed during hyperparameter tuning. Think of them as the standard tools or baseline settings in our machine learning "kitchen":

*   **Standard Measuring Cup:** The `BATCH_SIZE` defines how many pieces of data we process together in one step. We set a standard size for this.
*   **Default Oven Preheat:** If we aren't specifically tuning the learning rate for an optimizer like Adam or SGD, we might have a standard, default `LEARNING_RATE` to use as a starting point.

These constants provide:
1.  **Consistency:** Everyone uses the same value for these basic settings.
2.  **Baselines:** They offer default values, especially useful before we start fine-tuning hyperparameters.
3.  **Readability:** Instead of seeing a raw number like `32` scattered throughout the code, we see a meaningful name like `BATCH_SIZE`.

## Where We Define Constants: `constants.py`

In our `SC4002-Group-Assignment` project, we keep these fixed values together in a dedicated file called `constants.py`. This makes them easy to find and understand.

Let's look inside this file:

--- File: `constants.py` ---
```python
# Default number of samples processed in each training step
BATCH_SIZE = 32

# Default learning rate for the Adam optimizer
ADAM_LR = 0.001

# Default learning rate for the SGD optimizer
SGD_LR = 0.01
```

**Explanation:**

*   `BATCH_SIZE = 32`: This line sets a constant named `BATCH_SIZE` to the value `32`. This means that during training, our model will typically process data in groups of 32 sentences at a time. Why 32? It's a common default value that often balances computational speed and learning stability.
*   `ADAM_LR = 0.001`: This sets a constant for the default **L**earning **R**ate for an optimizer called "Adam". An optimizer helps the model learn by adjusting its internal parameters. The learning rate controls how big those adjustments are. `0.001` is a commonly used starting point for Adam.
*   `SGD_LR = 0.01`: Similarly, this sets the default learning rate for another optimizer called "SGD" (Stochastic Gradient Descent). `0.01` is a typical default for SGD.

These values are *constants* – they are defined once here and aren't expected to be changed by the tuning process itself. If we *were* tuning the learning rate (like we saw possible in [Chapter 2](02_tuning_hyperparameter_space.md)), the tuner would override this default value for specific trials. But if we aren't tuning it, or if we need a fixed batch size, we use these constants.

## How Constants Are Used in Code (Conceptual)

Other parts of our project's code can easily access these predefined constants. Here's a simplified, conceptual example of how `BATCH_SIZE` might be used when preparing data for training:

```python
# Conceptual Python code showing usage of constants

# 1. Import the constants from our special file
from constants import BATCH_SIZE, ADAM_LR

# (Imagine we have loaded our dataset: 'training_data')
# ... load data ...

# 2. Use the BATCH_SIZE constant when setting up the data loader
# This tells the loader to provide data in chunks of 32 samples.
data_loader = SomeDataLoader(dataset=training_data, batch_size=BATCH_SIZE)
print(f"Data will be processed in batches of size: {BATCH_SIZE}")

# 3. Use the ADAM_LR constant when setting up a default optimizer
# (If we weren't tuning the learning rate for this specific setup)
default_optimizer = tf.keras.optimizers.Adam(learning_rate=ADAM_LR)
print(f"Using default Adam optimizer with LR: {ADAM_LR}")

# ... rest of the training setup code ...
```

**Explanation:**

1.  We use `from constants import BATCH_SIZE, ADAM_LR` to bring the values defined in `constants.py` into our current script.
2.  When creating a `DataLoader` (a tool to feed data to the model), we pass `BATCH_SIZE` to its `batch_size` parameter. Now, the data loader knows to use the standard size of 32.
3.  When creating an Adam optimizer, we use `ADAM_LR` as the default learning rate.

This makes the code cleaner (`BATCH_SIZE` is more descriptive than `32`) and ensures we use the project's standard values.

## Constants vs. Hyperparameters: What's the Difference?

It's important to distinguish between Training Constants and the Hyperparameters we discussed in [Chapter 2](02_tuning_hyperparameter_space.md).

| Feature          | Training Constants (`constants.py`)             | Tunable Hyperparameters (`oracle.json` space) | Analogy                   |
| :--------------- | :---------------------------------------------- | :-------------------------------------------- | :------------------------ |
| **Purpose**      | Fixed, standard values for consistency/baseline | Settings to experiment with for optimization  | Standard measuring cup    | Variable recipe amount    |
| **Value Source** | Defined directly in `constants.py`              | Sampled from a range by the tuner           | Fixed tool size           | Chef's choice (within range) |
| **Variability**  | Stays the same across tuning trials             | Changes from one tuning trial to the next   | Always 1 cup              | Maybe 2 eggs, then 3 eggs |
| **Example**      | `BATCH_SIZE = 32`                               | `hp.Int("num_layers", 1, 4)`                  | Default preheat (180°C) | Testing 170°C vs 190°C    |

Training constants provide the stable foundation, while hyperparameters are the knobs we adjust during tuning to find the best performance.

## Conclusion

In this chapter, we learned about **Training Constants**:

*   They are **fixed numerical values** used throughout the training process (e.g., `BATCH_SIZE`, default learning rates like `ADAM_LR`).
*   They ensure **consistency**, provide **baselines**, and improve code **readability**.
*   They are typically defined in a central file like `constants.py`.
*   They are different from **hyperparameters**, which are *tuned* and varied during experiments. Constants remain fixed.

Think of them as the reliable, standard tools and settings in your ML kitchen, always there and always the same, allowing you to focus on adjusting the more experimental parts of your recipe (the hyperparameters).

Now that we understand the data shape, the tunable settings (hyperparameters), and the fixed settings (constants), how do we actually put this all together to start the tuning process?

Let's move on to the next chapter: [Hyperparameter Tuning Setup](04_hyperparameter_tuning_setup.md).

---

Generated by TEG SINGH TIWANA: [Cloud Assignment 2:Github LLM Codebase Knowledge Building Summarizer using Openai/Gemini/Claud](https://github.com/tej172/cloud_indv_assignments/tree/main/ass_2)