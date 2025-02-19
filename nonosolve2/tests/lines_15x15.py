lines = [
    {
        'line': [' ', ' ', ' ', ' ', ' ', ' ', ' ', 'X', 'X', ' ', ' ', ' ', ' ', ' ', ' '],
        'islands': [5],
        'result': """
|  |  |  |  |  |  |  |X |X |  |  |  |  |  |  | 5
 *  *  *  *  *  *  *        *  *  *  *  *  *   5
"""
    },
    {
        'line': [' ', ' ', 'X', ' ', ' ', ' ', ' ', 'X', 'X', ' ', ' ', ' ', ' ', ' ', ' '],
        'islands': [5],
        'result': """
|X |X |X |X |X |X |X |X |X |  |O |O |O |O |  | 5
                            *  *  *  *  *  *   5
"""
    },
    {
        'line': [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
        'islands': [13, 1],
        'result': """
|O |O |O |O |O |O |O |O |O |O |O |O |O |X |O | [13] [1]
 *  *  *  *  *  *  *  *  *  *  *  *  *         13
                                           *   1
"""
    },
    {
        'line': [' ', 'O', ' ', ' ', ' ', ' ', ' ', 'O', ' ', ' ', ' ', 'O', ' ', ' ', ' '],
        'islands': [1, 5],
        'result': """
|X |O |X |X |X |X |X |O |O |O |O |O |X |X |X | [1] [5]
    *                                          1
                      *  *  *  *  *            5
"""
    },
    {
        'line': [' ', ' ', ' ', 'O', ' ', ' ', ' ', 'O', 'O', ' ', ' ', ' ', ' ', ' ', ' '],
        'islands': [1, 1, 5, 2],
        'result': """
|  |  |X |O |X |  |  |O |O |O |  |  |  |  |  | 1 1 5 2
 *  *     *                                    1
          *     *                              1
                *  *  *  *  *  *  *            5
                                  *  *  *  *   2
"""
    },
    {
        'line': [' ', ' ', ' ', ' ', ' ', 'O', ' ', 'O', 'O', ' ', ' ', ' ', ' ', ' ', ' '],
        'islands': [4, 1],
        'result': """
|X |X |X |X |X |O |O |O |O |X |  |  |  |  |  | [4] 1
                *  *  *  *                     4
                               *  *  *  *  *   1
"""
    },
    {
        'line': [' ', ' ', ' ', ' ', ' ', ' ', ' ', 'O', 'O', ' ', ' ', ' ', ' ', ' ', ' '],
        'islands': [2, 2, 2],
        'result': """
|  |  |  |  |  |  |X |O |O |X |  |  |  |  |  | 2 2 2
 *  *  *  *  *  *     *  *                     2
          *  *  *     *  *     *  *            2
                      *  *     *  *  *  *  *   2
"""
    },
]