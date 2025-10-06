# If running standalone, load history from a file (e.g., history.pkl) or pass it from training script
try:
	import matplotlib.pyplot as plt
except ImportError:
	print("matplotlib is not installed. Please install it with 'pip install matplotlib'.")
	exit(1)

# Example: load history from pickle if not defined
import pickle
try:
	with open('history.pkl', 'rb') as f:
		history = pickle.load(f)
except Exception:
	print("Could not load history object. Please run training and save history, or pass it here.")
	history = None

if history:
	# Plot Accuracy
	plt.plot(history.history['accuracy'], label='Training Accuracy')
	plt.plot(history.history['val_accuracy'], label='Validation Accuracy')
	plt.xlabel('Epochs')
	plt.ylabel('Accuracy')
	plt.title('Training vs Validation Accuracy')
	plt.legend()
	plt.show()

	# Plot Loss
	plt.plot(history.history['loss'], label='Training Loss')
	plt.plot(history.history['val_loss'], label='Validation Loss')
	plt.xlabel('Epochs')
	plt.ylabel('Loss')
	plt.title('Training vs Validation Loss')
	plt.legend()
	plt.show()
else:
	print("No history object available for plotting.")
