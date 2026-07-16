# User Guide — AI Dermatology Diagnostic Support

A step-by-step guide for health workers using the AI diagnostic tool to assist with skin condition assessment.

---

## Table of Contents

1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Uploading an Image](#uploading-an-image)
4. [Understanding the Results](#understanding-the-results)
5. [Providing Feedback](#providing-feedback)
6. [Supported Conditions](#supported-conditions)
7. [Important Limitations](#important-limitations)
8. [Troubleshooting](#troubleshooting)

---

## Introduction

The AI Dermatology Diagnostic Support tool helps non-specialist health workers assess skin conditions at the point of care. It uses an AI model trained on dermatological images to provide:

- A **predicted condition** (one of 7 supported diagnoses)
- A **confidence score** (how certain the AI is)
- A **clinical note** with relevant background information
- A **referral recommendation** guiding next steps

> **This tool is a decision-support aid. It does NOT replace clinical judgment.** Always use your professional expertise alongside the AI's suggestion.

---

## Getting Started

1. Open a web browser on your phone, tablet, or computer.
2. Navigate to the application URL provided by your facility administrator (e.g., `http://diagnostic.yourfacility.com`).
3. You will see the upload screen.

### Browser Compatibility

The tool works on any modern browser:
- Google Chrome (recommended)
- Mozilla Firefox
- Microsoft Edge
- Safari (iOS/macOS)

---

## Uploading an Image

### Step 1: Select an Image

Click or tap the **"Choose File"** button and select a photo of the skin condition. You can:

- **Take a photo** directly from your device's camera
- **Select an existing photo** from your gallery or file system

### Supported Formats

| Format | Extension |
| ------ | --------- |
| JPEG   | `.jpg`, `.jpeg` |
| PNG    | `.png`    |
| WebP   | `.webp`   |

**Maximum file size:** 8 MB

### Step 2: Add Optional Metadata (Recommended)

Before clicking "Analyze," you may optionally fill in:

- **Facility Name** — The name of your clinic or health centre (e.g., "Lagos General Hospital").
- **Region / State** — The state or region where you are located (e.g., "Lagos", "Abuja").

This metadata is used for epidemiological tracking and helps public health officials understand condition distribution. **No patient-identifying information is collected.**

### Step 3: Submit for Analysis

Click the **"Analyze Image"** button. A loading screen will appear while the AI processes your image. This typically takes 5–15 seconds depending on server load.

---

## Understanding the Results

After processing, you will see a results page with:

### 1. Predicted Condition

The AI's best guess for the skin condition (e.g., "Eczema", "Melanoma").

### 2. Confidence Score

A percentage indicating how certain the AI is about its prediction:

| Confidence  | Meaning                                           |
| ----------- | ------------------------------------------------- |
| **80–100%** | High confidence — the AI is fairly sure            |
| **60–79%**  | Moderate confidence — consider with clinical signs  |
| **Below 60%** | Low confidence — exercise extra caution          |

### 3. Clinical Note

Background information about the predicted condition, including common symptoms and characteristics.

### 4. Referral Recommendation

Guidance on whether and when to refer the patient to a specialist. Urgency varies by condition — for example, suspected Melanoma always recommends urgent referral.

### 5. Demo Mode Notice

If the system is running in demo mode (for training or testing purposes), a clear notice will be displayed. Demo mode results are **not based on a real AI model** and should not be used for clinical decisions.

---

## Providing Feedback

After reviewing the results, you can help improve the system by providing feedback:

### Star Rating (1–5)

Rate how helpful the AI's diagnosis was:

| Stars | Meaning                         |
| ----- | ------------------------------- |
| ⭐     | Not at all helpful               |
| ⭐⭐   | Slightly helpful                 |
| ⭐⭐⭐  | Moderately helpful               |
| ⭐⭐⭐⭐ | Very helpful                     |
| ⭐⭐⭐⭐⭐| Extremely helpful — spot-on      |

### Clinical Override

If the AI's prediction does not match your clinical assessment, type your own diagnosis in the **"Clinical Override"** text box. For example:

> "Patient presents with contact dermatitis, not eczema. Exposure to new soap reported."

This feedback is invaluable for improving the model over time.

Click **"Submit Feedback"** to save your response. You will see a green confirmation message.

---

## Supported Conditions

| Condition       | Description                                                         |
| --------------- | ------------------------------------------------------------------- |
| Melanoma        | Potentially serious skin cancer requiring prompt assessment          |
| Eczema          | Inflammatory condition with itching, dryness, and recurrent flares   |
| Psoriasis       | Chronic inflammatory condition producing scaly plaques               |
| Acne Vulgaris   | Blocked follicles with inflammation, papules, or nodules             |
| Tinea/Ringworm  | Fungal infection with itchy, ring-shaped patches                     |
| Vitiligo        | Pigmentary disorder causing depigmented patches                      |
| Monkeypox       | Viral illness with fever and characteristic skin lesions             |

---

## Important Limitations

1. **Not a replacement for clinical judgment.** The AI provides suggestions — the final diagnosis is always yours.
2. **Limited to 7 conditions.** If the patient's condition is not one of the 7 supported diagnoses, the AI will still classify it as one of them. Be aware of this limitation.
3. **Image quality matters.** Blurry, poorly lit, or obstructed images will reduce accuracy. Take clear, well-lit photos of the affected area.
4. **No patient data is stored.** The system does not save patient names, IDs, or images. Only anonymized diagnostic statistics are recorded.
5. **Requires internet access.** The tool requires a connection to the server running the AI model.

---

## Troubleshooting

### "Please upload a valid image"

- Make sure your file is a JPG, PNG, or WebP image.
- Check that the file size is under 8 MB.
- Try taking a new photo with better lighting.

### The page is stuck on "Processing..."

- The AI model may be under heavy load. Wait 30 seconds and refresh.
- If the issue persists, try uploading the image again.
- Contact your facility administrator if the problem continues.

### "An internal error occurred"

- The server may be temporarily unavailable.
- Try again in a few minutes.
- If the error persists, contact your system administrator.

### Feedback submission shows an error

- Check your internet connection.
- Try clicking "Submit Feedback" again.
- The feedback may have already been saved — check for a confirmation message.

---

## Quick Reference Card

```
1. Open the diagnostic tool in your browser.
2. Select or capture a photo of the skin condition.
3. (Optional) Enter your facility name and region.
4. Click "Analyze Image."
5. Review the predicted condition, confidence, and referral advice.
6. Provide a star rating and clinical override if needed.
7. Click "Submit Feedback."
```

> **Remember:** This tool supports your clinical expertise — it does not replace it.
