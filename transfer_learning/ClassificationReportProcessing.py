"""
This program undertakes the processing of classification reports
which are generated by Scikit Learn during classification evaluation.
Version: 11/08/2020
"""
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def load_report(csv_path: str) -> pd.DataFrame :
    """
    This function loads the classification report .csv as a Pandas DataFrame.
    :param csv_path: Path to .csv classification report file
    :return: Pandas DataFrame of the classification report
    """
    classification_report = pd.read_csv(csv_path)
    classification_report.columns = ["Cities", "Precision", "Recall", "F1_Score", "Support"]
    classification_report = classification_report[:-3]  # Gets rid of the Non cities stats at the bottom of the .csv

    return classification_report


def plot_f1(classification_report: pd.DataFrame, csv_name: str) -> None:
    """
    This function plots a bar chart of the F1 score.
    :param classification_report: Classification report Pandas DataFrame.
    :param csv_name: Path to .csv taken from standard input is processed into a plot name.
    :return:
    """
    name = csv_name.split("/")[2].split("_")[0] + " " + csv_name.split("_")[2].upper() + " F1 Score"
    if "VGG-19" in name:
        name = csv_name.split("/")[2].split("_")[0] + " " + csv_name.split("_")[2].upper() + " F1 Score"
    plt.figure(figsize=(10, 5))
    plt.tight_layout()
    bars = np.arange(len(classification_report))
    plt.bar(bars, classification_report["F1_Score"], width=0.9, color="orange")
    plt.title(name)
    plt.xticks(bars, classification_report["Cities"], rotation=90, fontsize=5)
    plt.ylabel("F1 Score")
    plt.xlabel("Cities")
    plt.xlim(-0.5, len(classification_report["Cities"]) - 0.5)
    plt.savefig("../visualisations/f1_scores/" + name.replace(" ", "_") + ".png", bbox_inches="tight")

    return


def main():
    plt.style.use("ggplot")

    classification_report = load_report(sys.argv[1])
    plot_f1(classification_report=classification_report, csv_name=sys.argv[1])

    return


if __name__ == "__main__":
    main()