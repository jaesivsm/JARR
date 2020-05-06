common_stopwords = {'news'}

extra_stopwords = {
    'french': {'afp', 'flash', 'actual', 'actu', 'info',
               'nouvel', 'dépech', 'brev', 'depech'}.union(common_stopwords),
    'english': common_stopwords,
    'german': common_stopwords,
    'spanish': common_stopwords,
}
