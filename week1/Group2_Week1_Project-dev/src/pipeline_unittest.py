import unittest
from unittest.mock import patch
import main

class TestMainPipeline(unittest.TestCase):

    @patch('main.load_data')
    @patch('main.clean_data')
    @patch('main.save_cleaned_data')
    @patch('main.show_basic_info')
    @patch('main.plot_correlation_matrix')
    @patch('main.plot_distributions')
    @patch('main.plot_categorical_counts')
    @patch('main.train_model')
    def test_main_pipeline(self, mock_train, mock_plot_cat, mock_plot_dist, mock_corr, mock_info, mock_save, mock_clean, mock_load):
        # Setup mock returns
        mock_load.return_value = "raw_df"
        mock_clean.return_value = "clean_df"
        mock_train.return_value = "trained_model"

        # Call main
        main.main()

        # Check if functions are called
        mock_load.assert_called_once_with('data/raw/Titanic dataset.csv')
        mock_clean.assert_called_once_with("raw_df")
        mock_info.assert_called_once_with("clean_df")
        mock_corr.assert_called_once_with("clean_df")
        mock_plot_dist.assert_called_once_with("clean_df")
        mock_plot_cat.assert_called_once_with("clean_df", column='survived')
        mock_train.assert_called_once_with("clean_df", target_column='survived')

if __name__ == '__main__':
    unittest.main()
