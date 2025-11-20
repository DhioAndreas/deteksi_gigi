import os
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.utils import class_weight
import tensorflow as tf
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping, ReduceLROnPlateau

# --- Konfigurasi ---
DATASET_DIR = 'C:/deteksi_gigi/dataset'
IMG_HEIGHT = 224
IMG_WIDTH = 224
BATCH_SIZE = 32
TOTAL_EPOCHS = 40
MODEL_SAVE_PATH = 'best_model.h5'
CONFIDENCE_THRESHOLD = 0.7

# --- Augmentasi Data dengan strategi khusus ---
train_datagen = ImageDataGenerator(
    rescale=1./255,
    rotation_range=20,
    width_shift_range=0.15,
    height_shift_range=0.15,
    shear_range=0.15,
    zoom_range=0.2,
    horizontal_flip=True,
    fill_mode='nearest',
    brightness_range=[0.7, 1.3],
    channel_shift_range=60.0
)

val_datagen = ImageDataGenerator(rescale=1./255)

# --- Data Generator ---
train_generator = train_datagen.flow_from_directory(
    os.path.join(DATASET_DIR, 'train'),
    target_size=(IMG_HEIGHT, IMG_WIDTH),
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    shuffle=True
)

validation_generator = val_datagen.flow_from_directory(
    os.path.join(DATASET_DIR, 'validation'),
    target_size=(IMG_HEIGHT, IMG_WIDTH),
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    shuffle=False
)

# --- Info Kelas ---
NUM_CLASSES = train_generator.num_classes
class_names = list(train_generator.class_indices.keys())
print(f"\n✅ Kelas terdeteksi: {train_generator.class_indices}")
print(f"✅ Jumlah kelas: {NUM_CLASSES}")

# --- Hitung class_weight untuk balance ---
class_weights_array = class_weight.compute_class_weight(
    class_weight='balanced',
    classes=np.unique(train_generator.classes),
    y=train_generator.classes
)
class_weights = dict(enumerate(class_weights_array))
print(f"\n⚖️ Class Weights: {class_weights}")

# --- Model ---
base_model = MobileNetV2(input_shape=(IMG_HEIGHT, IMG_WIDTH, 3), include_top=False, weights='imagenet')
for layer in base_model.layers[:-50]:  # Fine-tune lebih banyak layer
    layer.trainable = False

x = base_model.output
x = GlobalAveragePooling2D()(x)
x = Dense(128, activation='relu')(x)
x = Dropout(0.4)(x)
output = Dense(NUM_CLASSES, activation='softmax')(x)

model = Model(inputs=base_model.input, outputs=output)

model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=1e-4),
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

model.summary()

# --- Callbacks ---
checkpoint_cb = ModelCheckpoint(MODEL_SAVE_PATH, monitor='val_accuracy', mode='max', save_best_only=True, verbose=1)
early_stopping_cb = EarlyStopping(monitor='val_accuracy', patience=10, restore_best_weights=True, verbose=1)
reduce_lr_cb = ReduceLROnPlateau(monitor='val_accuracy', factor=0.2, patience=3, min_lr=1e-7, verbose=1)

# --- Training ---
print("\n🚀 Training model dengan augmentasi & class_weight...")
history = model.fit(
    train_generator,
    epochs=TOTAL_EPOCHS,
    validation_data=validation_generator,
    steps_per_epoch=train_generator.samples // BATCH_SIZE,
    validation_steps=validation_generator.samples // BATCH_SIZE,
    callbacks=[checkpoint_cb, early_stopping_cb, reduce_lr_cb],
    class_weight=class_weights
)

print(f"\n✅ Model terbaik disimpan sebagai '{MODEL_SAVE_PATH}'")

# --- Evaluasi ---
print("\n🔍 Evaluasi performa model...")
val_generator_eval = val_datagen.flow_from_directory(
    os.path.join(DATASET_DIR, 'validation'),
    target_size=(IMG_HEIGHT, IMG_WIDTH),
    batch_size=1,
    class_mode='categorical',
    shuffle=False
)

preds = model.predict(val_generator_eval, steps=val_generator_eval.samples)
y_pred = np.argmax(preds, axis=1)
y_true = val_generator_eval.classes

# Confusion Matrix
cm = confusion_matrix(y_true, y_pred)
print("\n📊 Confusion Matrix:")
print(cm)

# Classification Report
report = classification_report(y_true, y_pred, target_names=class_names)
print("\n📄 Classification Report:")
print(report)