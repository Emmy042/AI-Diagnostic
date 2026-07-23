# Training Your AI Model on Google Colab (with Kaggle Datasets)

Since training an image classification model locally can take a massive amount of CPU/GPU power, **Google Colab** is the perfect solution. It gives you a free cloud computer with a powerful GPU. 

Here is exactly how to train your model in Colab using data directly from Kaggle, and then bring it back to your local Flask app.

## Step 1: Prepare your Kaggle API Key
To download datasets directly into Colab, you need a Kaggle API token.
1. Go to [Kaggle.com](https://www.kaggle.com/) and log in (or sign up).
2. Click your profile picture in the top right -> **Settings**.
3. Scroll down to the **API** section and click **Create New Token**.
4. A file named `kaggle.json` will download to your computer. Keep it handy.

## Step 2: Set up Google Colab
1. Go to [Google Colab](https://colab.research.google.com/) and create a **New Notebook**.
2. At the top menu, click **Runtime** -> **Change runtime type**.
3. Under **Hardware accelerator**, select **T4 GPU** and save. This makes training 10x faster.

## Step 3: Run the Training Code
Colab uses "cells" for code. You will paste the code below into Colab cells and run them one by one.

### Cell 1: Upload Kaggle API Key
Paste this into the first cell and click the **Play** button. It will ask you to upload a file. Upload your `kaggle.json` file.
```python
from google.colab import files
import os

print("Please upload your kaggle.json file:")
files.upload()

# Move the kaggle.json file to the correct hidden folder
!mkdir -p ~/.kaggle
!cp kaggle.json ~/.kaggle/
!chmod 600 ~/.kaggle/kaggle.json
```

### Cell 2: Download a Dataset
Find a skin disease dataset on Kaggle. For example, if the URL is `kaggle.com/datasets/ismailpromih/skin-diseases-image-dataset`, the dataset identifier is `ismailpromih/skin-diseases-image-dataset`.

Run this cell to download and unzip it directly into Colab:
```bash
!kaggle datasets download -d ismailpromih/skin-diseases-image-dataset
!unzip -q skin-diseases-image-dataset.zip -d dataset/
```
*(Note: You will need to write a little code to reorganize the folders to match your 7 exact classes if the Kaggle dataset uses different names).*

### Cell 3: Install Dependencies & Upload Training Script
```python
!pip install -q scikit-learn tqdm
```

### Cell 4: Run the Training Script
Upload `colab_trainer.py` from your project to Colab (use the file browser on the left, or drag-and-drop), then run it:
```python
!python colab_trainer.py
```

The script will:
1. Download and consolidate both Kaggle datasets
2. **Balance classes** (capped at 2000 images each to prevent bias)
3. Train in two phases — frozen base, then fine-tuning top layers
4. Print a **Classification Report** at the end so you can verify no single class dominates predictions

> **⚠️ Check the report!** If any class shows > 50% of all predictions, the model is still biased and needs more data for underrepresented classes.

## Step 4: Download and Run Locally
1. Once the training finishes, look at the **Files** menu on the far left side of Google Colab (the folder icon).
2. You will see `derma_inceptionv3.keras`.
3. Click the three dots next to it and select **Download**.
4. Move this downloaded file directly into your `C:\Users\Nuel0\Documents\AI-Diagnostic` folder, overwriting the broken one.
5. Stop your running Flask server (`Ctrl + C`) and start it again with `python run.py`. 

Your application will now be running a real, functional ML model trained by Google's cloud GPUs!
