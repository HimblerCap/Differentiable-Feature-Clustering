import argparse
import tensorflow as tf

from loss import CustomLoss
from utils import plot_pictures, inference, load_image, preprocessing
from diff_feature_model import DiffFeatureModel
from pathlib import Path
import os

MODELS_PATH = os.path.join(Path(__file__).parent.parent, 'models')

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--save_model", type=str, help='path in where you want to save your model', required=True)
    parser.add_argument("-p", type=int, default=100, help='filters of Conv2D', required=False)
    parser.add_argument("-q", type=int, default=100, help='filters of Conv1D', required=False)
    parser.add_argument("-M", type=int, default=3, help='numbers of convolution layers', required=False)
    parser.add_argument("-mu", type=float, default=5, help='mu value of or loss function', required=False)
    parser.add_argument("-lr", type=float, default=0.1, help='learning rate', required=False)
    parser.add_argument("-momentum", type=float, default=0.9, help='momentum of SGD', required=False)
    parser.add_argument("-epochs", type=int, default=500, help='number of epochs', required=False)
    args = parser.parse_args()
    image = load_image()
    data, width, height = preprocessing(image)

    # Parameters of our neural network
    p = args.p
    q = args.q
    M = args.M

    u = args.mu
    lr = args.lr
    momentum = args.momentum
    epochs = args.epochs

    # Create a model
    model = DiffFeatureModel(img_shape=[width, height], p=p, q=q, m=M)

    # View the structure of our model
    model.summary()

    # Optimizer and Loss
    optimizer = tf.keras.optimizers.SGD(learning_rate=lr, momentum=momentum)
    loss = CustomLoss(mu=u, q=q, width=width, height=height)

    model.compile(optimizer=optimizer, loss=loss, metrics=[loss.continuity_loss, loss.feat_sim_loss])

    # Train our model
    earlystopping = tf.keras.callbacks.EarlyStopping(monitor='loss', patience=15)
    model.fit(data, epochs=epochs, callbacks=[earlystopping])

    # Save your model
    model.save(os.path.join(MODELS_PATH, args.save_model))

    # Predict image
    image_segmented = inference(model, data)

    # Plot our result and real image
    plot_pictures(predict_image=image_segmented, real_image=image)
