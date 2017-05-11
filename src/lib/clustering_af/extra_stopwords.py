common_stopwords = {'youtube', 'reddit', 'reddit.com'}

extra_stopwords = {
    'french': {'les', 'afp', 'quand'}.union(common_stopwords),
    'english': common_stopwords,
    'german': common_stopwords,
    'spanish': common_stopwords,
}
