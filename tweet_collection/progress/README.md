# Progress files

This directory will contain a text file and a pickle that will record the dates for which tweets have been collected from the Twitter API, processed, and saved to the `twitter_data` directory. 

The pickles (`dates_saved_uk.pkl` and  `dates_saved_eu.pkl`) are produced and used by the scripts in the `code` directory; the pickles contain all the dates for which Twitter data has been saved to the `twitter_data` directory (it also includes country data for tweets from European Union countries). The pickles are thus used to set a start date for tweet collection every time a script is run anew. Scripts must be run anew when they produce the `HTTP Error code: 429` ("Too Many Requests"), which indicates that the Twitter API rate limits have been met (for the Twitter academic API, tweet collection is limited to 10 million tweets per month, per user).

The text file (`dates_collected.txt`) is produced by the scripts in the `code` directory; it can be used to manually check progress.  
