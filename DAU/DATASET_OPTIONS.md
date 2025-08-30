# 🌿 Mangrove Dataset Options & Training Guide

## 📊 **Current Status: NO DATASET AVAILABLE**

The system is currently using **random weights** because no training dataset exists. Here are the options to get real data:

---

## 🎯 **Option 1: Public Datasets (Recommended)**

### **1.1 Global Mangrove Watch Dataset**
- **Source**: Global Mangrove Watch (GMW)
- **Coverage**: Global mangrove extent maps
- **Format**: GeoTIFF raster data
- **Resolution**: 25m
- **Years**: 1996-2020
- **Access**: https://www.globalmangrovewatch.org/

### **1.2 Sentinel-2 Mangrove Dataset**
- **Source**: ESA Copernicus
- **Coverage**: Global
- **Format**: Multispectral imagery
- **Resolution**: 10m
- **Access**: https://scihub.copernicus.eu/

### **1.3 USGS Earth Explorer**
- **Source**: US Geological Survey
- **Coverage**: Global
- **Format**: Landsat, aerial imagery
- **Access**: https://earthexplorer.usgs.gov/

### **1.4 Google Earth Engine**
- **Source**: Google
- **Coverage**: Global
- **Format**: Multiple satellite sources
- **Access**: https://earthengine.google.com/

---

## 🛠️ **Option 2: Create Custom Dataset**

### **2.1 Data Collection Strategy**
```python
# Example data collection script
import requests
from datetime import datetime
import os

def collect_mangrove_images():
    """Collect mangrove images from multiple sources."""
    
    # 1. Download from public APIs
    sources = [
        "https://api.globalmangrovewatch.org/",
        "https://scihub.copernicus.eu/",
        "https://earthexplorer.usgs.gov/"
    ]
    
    # 2. Scrape from research papers
    # 3. Use citizen science platforms
    # 4. Partner with research institutions
```

### **2.2 Annotation Process**
```python
# Example annotation workflow
def create_annotations():
    """Create segmentation masks and labels."""
    
    # 1. Manual annotation using tools like:
    #    - LabelMe
    #    - VGG Image Annotator
    #    - Supervisely
    #    - Roboflow
    
    # 2. Semi-automated annotation
    #    - Use pre-trained models for initial masks
    #    - Human verification and correction
    
    # 3. Quality control
    #    - Multiple annotators
    #    - Inter-annotator agreement
```

---

## 📋 **Option 3: Use Pre-trained Models**

### **3.1 Transfer Learning Approach**
```python
# Example: Use pre-trained models
from torchvision.models import segmentation

def load_pretrained_model():
    """Load pre-trained segmentation model."""
    
    # Use DeepLabV3+ pre-trained on COCO
    model = segmentation.deeplabv3_resnet101(
        pretrained=True,
        progress=True,
        num_classes=21
    )
    
    # Fine-tune for mangrove segmentation
    # Replace final layer for binary classification
    model.classifier[-1] = torch.nn.Conv2d(256, 1, kernel_size=1)
    
    return model
```

### **3.2 Available Pre-trained Models**
- **DeepLabV3+**: Good for semantic segmentation
- **U-Net**: Excellent for medical/biological images
- **SegNet**: Efficient for real-time applications
- **PSPNet**: Good for complex scenes

---

## 🎯 **Recommended Immediate Action Plan**

### **Phase 1: Quick Start (1-2 weeks)**
1. **Download Global Mangrove Watch data**
   ```bash
   # Download mangrove extent maps
   wget https://data.unep-wcmc.org/datasets/45
   ```

2. **Use Sentinel-2 imagery**
   ```python
   # Use sentinelhub-py for data access
   from sentinelhub import SentinelHubRequest, DataCollection
   
   request = SentinelHubRequest(
       data_collection=DataCollection.SENTINEL2_L2A,
       bands=['B02', 'B03', 'B04', 'B08'],  # RGB + NIR
       bbox=bbox,
       time_interval=time_interval,
       size=size
   )
   ```

3. **Create minimal training set**
   - 100-500 annotated images
   - Focus on high-quality, diverse samples

### **Phase 2: Scale Up (1-2 months)**
1. **Expand dataset to 1000+ images**
2. **Add multiple mangrove species**
3. **Include different seasons/conditions**
4. **Add anomaly examples**

### **Phase 3: Production Ready (3-6 months)**
1. **10,000+ annotated images**
2. **Multiple geographic regions**
3. **Comprehensive validation set**
4. **Continuous data pipeline**

---

## 📊 **Dataset Requirements**

### **Minimum Viable Dataset:**
- **Training**: 500 images
- **Validation**: 100 images  
- **Test**: 100 images
- **Total**: 700 images

### **Production Dataset:**
- **Training**: 10,000+ images
- **Validation**: 1,000+ images
- **Test**: 1,000+ images
- **Total**: 12,000+ images

### **Image Requirements:**
- **Resolution**: 256x256 to 1024x1024 pixels
- **Format**: JPEG, PNG, GeoTIFF
- **Channels**: RGB (3) or Multispectral (4-13)
- **Quality**: Clear, well-lit, minimal cloud cover

---

## 🛠️ **Implementation Steps**

### **Step 1: Set up data collection**
```bash
# Create dataset directory structure
mkdir -p mangrove_dataset/{images,annotations,splits}
mkdir -p mangrove_dataset/images/{satellite,aerial,ground}
mkdir -p mangrove_dataset/annotations/{masks,labels}
```

### **Step 2: Download public data**
```python
# Example: Download Global Mangrove Watch data
import geopandas as gpd
import rasterio
from rasterio.mask import mask

# Load mangrove extent shapefile
mangrove_gdf = gpd.read_file("gmw_v3_2020_vector.gpkg")

# Download corresponding satellite imagery
# Process and create training pairs
```

### **Step 3: Create annotations**
```python
# Example: Create segmentation masks
import cv2
import numpy as np

def create_segmentation_mask(image_path, annotation_path):
    """Create binary segmentation mask from annotation."""
    
    # Load image and annotation
    image = cv2.imread(image_path)
    annotation = load_annotation(annotation_path)
    
    # Create binary mask
    mask = np.zeros(image.shape[:2], dtype=np.uint8)
    
    # Fill mangrove areas
    cv2.fillPoly(mask, [annotation], 255)
    
    return mask
```

### **Step 4: Train the model**
```python
# Example: Training script
def train_mangrove_model():
    """Train mangrove segmentation model."""
    
    # Load dataset
    train_dataset = MangroveDataset("train")
    val_dataset = MangroveDataset("validation")
    
    # Create model
    model = SwinUMambaMangrove()
    
    # Train
    trainer = Trainer(
        model=model,
        train_dataset=train_dataset,
        val_dataset=val_dataset,
        epochs=100,
        batch_size=8
    )
    
    trainer.train()
```

---

## 📈 **Expected Results**

### **With Minimal Dataset (500 images):**
- **Accuracy**: 70-80%
- **Use Case**: Proof of concept, basic validation

### **With Production Dataset (10,000+ images):**
- **Accuracy**: 90-95%
- **Use Case**: Production deployment, reliable monitoring

---

## 🔗 **Useful Resources**

### **Data Sources:**
- [Global Mangrove Watch](https://www.globalmangrovewatch.org/)
- [ESA Copernicus](https://www.copernicus.eu/)
- [USGS Earth Explorer](https://earthexplorer.usgs.gov/)
- [Google Earth Engine](https://earthengine.google.com/)

### **Annotation Tools:**
- [LabelMe](https://github.com/wkentaro/labelme)
- [VGG Image Annotator](http://www.robots.ox.ac.uk/~vgg/software/via/)
- [Supervisely](https://supervisely.com/)
- [Roboflow](https://roboflow.com/)

### **Research Papers:**
- "Deep Learning for Mangrove Mapping" - IEEE GRSM 2021
- "MangroveNet: A Deep Learning Framework" - Remote Sensing 2020
- "Global Mangrove Watch v3" - Remote Sensing 2021

---

## 🎯 **Next Steps**

1. **Choose a data source** (recommend Global Mangrove Watch)
2. **Download sample data** (100-200 images)
3. **Create basic annotations** (manual or semi-automated)
4. **Train initial model** (transfer learning approach)
5. **Evaluate performance** and iterate

Would you like me to help you implement any of these options?
