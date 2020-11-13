"""
This script evaluates the model performance on unseen (testing) dataset.
It calculates the Top-1 and Top-5 predictions and gets the percentage of
correct predictions which were achieved.
Version 07/08/2020
"""
import os
import sys
import numpy as np
import torch
import torchvision as vision
import pandas as pd
from sklearn import metrics
import matplotlib.pyplot as plt
from torch.utils.data import DataLoader
from TrainModels import initialise_model
from typing import Tuple, Dict, List


def load_testing_set_and_transform(testing_set_path: str, uses_inception: bool) -> Tuple[Dict, List]:
    """
    This function creates a dataloader for the testing set and preprocesses the data
    in order to fit the pretrained network architecture.
    :param testing_set_path:
    :param uses_inception:
    :return: testing_loader - test set dataloader, classes - classes from which to predict.
    """
    if uses_inception:
        input_size = 299
    else:
        input_size = 224

    transformations = {
        "test": vision.transforms.Compose([
            vision.transforms.CenterCrop(input_size),
            vision.transforms.ToTensor(),
            vision.transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
    }

    testing_set = {image: vision.datasets.ImageFolder(os.path.join(testing_set_path, image),
                                                      transformations[image]) for image in ["test"]}
    testing_loader = {image: DataLoader(testing_set[image], batch_size=1, shuffle=True, num_workers=4)
                      for image in ["test"]}

    classes = testing_set["test"].classes
    
    return testing_loader, classes


def make_predictions(testing_loader, classes, model, trained_weights) -> Tuple[List, List]:
    """
    This function makes inference and predicts the classes for a given image.
    :param testing_loader: PyTorch Data Loader of the testing set
    :param classes: List of possible classes
    :param model: Trained PyTorch model
    :param trained_weights: Trained model weights
    :return:
    """
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    model = initialise_model(model_name=model, num_classes=len(classes), freeze_all=False)[0]
    model.load_state_dict(torch.load(trained_weights))
    model.to(device)
    
    with torch.no_grad():
        model.eval()
        top_1_accuracy = 0
        top_5_accuracy = 0
        #  Confusion Matrix variables
        all_ground_truth = []
        all_predictions = []

        for inputs, labels in testing_loader["test"]:
            inputs = inputs.to(device)
            outputs = model(inputs)
            outputs = outputs.to(device)
            outputs = torch.exp(outputs)
            predictions = outputs.data.cpu()
            prediction_top_1 = np.argmax(predictions.numpy())
            prediction_top_5 = predictions.topk(5, dim=1)[1]
            all_ground_truth.append(classes[torch.max(labels).item()])
            all_predictions.append(classes[prediction_top_1])

            if classes[torch.max(labels).item()] == classes[prediction_top_1]:
                top_1_accuracy += 1
            
            if torch.max(labels).item() in prediction_top_5:
                top_5_accuracy += 1
 
        test_accuracy_top_1 = (top_1_accuracy/len(testing_loader["test"]))*100
        test_accuracy_top_5 = (top_5_accuracy/len(testing_loader["test"]))*100
        
        print("Testing accuracy (Top-1): {:.2f}".format(test_accuracy_top_1))
        print("Testing accuracy (Top-5): {:.2f}".format(test_accuracy_top_5))
        
    return all_ground_truth, all_predictions


def create_confusion_matrix(ground_truth, predictions, classes, generate_report, title) -> np.ndarray:
    """
    This function creates a confusion matrix for the given ground truth (true labels) and
    predictions generated by the classifier.
    :return: Confusion matrix - Matrix with the amount of true/false predictions.
    """    
    conf_matrix = metrics.confusion_matrix(ground_truth, predictions, labels=classes)
    
    plt.figure(figsize=(12, 12))
    plt.imshow(conf_matrix, cmap="jet")
    plt.colorbar()
    ticks = np.arange(len(classes))
    plt.xticks(ticks, classes, rotation=90)
    plt.yticks(ticks, classes)
    plt.ylim(-0.5, len(classes))
    plt.title(title)
    plt.savefig("../visualisations/confusion_matrices/" + title + "_Confusion_Matrix.png")
    
    if generate_report:
        report = metrics.classification_report(ground_truth, predictions, labels=classes, output_dict=True)
        report_to_pandas = pd.DataFrame(report).transpose()
        report_to_pandas.to_csv("./classification_reports/" + title + "_rgb_classification_report_.csv")
    
    return conf_matrix


def main():
    model = sys.argv[1]
    print("Evaluating Model: " + model)

    if model == "InceptionV3":
        uses_inception = True
    else:
        uses_inception = False

    testing_loader, classes = load_testing_set_and_transform(sys.argv[2], uses_inception=uses_inception)
    ground_truth, predictions = make_predictions(testing_loader=testing_loader, classes=classes,
                                                 model=model, trained_weights=sys.argv[3])
    create_confusion_matrix(ground_truth=ground_truth, predictions=predictions, classes=classes,
                            generate_report=True, title=model)
        
    return


if __name__ == "__main__":
    main()

