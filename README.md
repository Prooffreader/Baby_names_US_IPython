Baby_names_US_IPython
=====================

A set of IPython notebooks to help analyze the US Social Security Administration baby names database

### U.S. Baby names iPython notebooks #

  * By David Taylor, [www.prooffreader.com](http://www.prooffreader.com)
  * Uses data from United States Social Security Administration; with some minor adjustments, it should be easily convertible to use other data sets.
  * Uses IPython notebooks to facilitate interactive exploration
  * Published on Github in case it can be useful to anyone who wishes to explore this or a similar dataset.
  * Feedback, positive or negative, is welcome.

Explanation of notebooks with links to nbviewer versions:

*  [download_and_process.ipynb](http://nbviewer.ipython.org/github/Prooffreader/Baby_names_US_IPython/blob/master/download_and_process.ipynb) Downloads and makes pandas dataframe from US SSA baby names data
*  [charting.ipynb](http://nbviewer.ipython.org/github/Prooffreader/Baby_names_US_IPython/blob/master/charting.ipynb) Several cells to make several types of charts from the data
*  [last_letter_boys_names.ipynb](http://nbviewer.ipython.org/github/Prooffreader/Baby_names_US_IPython/blob/master/last_letter_boys_names.ipynb) Script to make histograms of last letters in boys' names to show the incredible rise of '-n'. [Blog post about it](http://www.prooffreader.com/2014/04/baby-names-rise-of-n.html) became wildly popular.
*  [letter_freqs_and_bigrams.ipynb](http://nbviewer.ipython.org/github/Prooffreader/Baby_names_US_IPython/blob/master/letter_freqs_and_bigrams.ipynb) In progress, to find frequency of letters and letter pairs in baby names
*  [singletons.ipynb](http://nbviewer.ipython.org/github/Prooffreader/Baby_names_US_IPython/blob/master/singletons.ipynb) In progress, to find names that only appear in the database once.
*  [trendiness.ipynb](http://nbviewer.ipython.org/github/Prooffreader/Baby_names_US_IPython/blob/master/trendiness.ipynb) To determine trendiest names (with an popular, not mathematic definition of trendy) using an analytical chemistry data analysis technique. The [blog post about it](http://www.prooffreader.com/2014/07/trendiest-baby-names-in-social-security.html) was *insanely* popular, which I did not at all predict!

*note: download_and_process.py is simply the .py export of download_and_process.ipynb, so it can be called by other notebooks to load the data.*
