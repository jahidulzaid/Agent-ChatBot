def draw_snake(n, m):
    result = []
    for i in range(n):
        if i % 2 == 0:  # Odd row (0, 2, 4... in 0-indexing)
            result.append('#' * m)
        else:  # Even row (1, 3, 5... in 0-indexing)
            if (i // 2) % 2 == 0:  # 2nd, 6th... (0-indexed)
                result.append('.' * (m - 1) + '#')
            else:  # 4th, 8th... (0-indexed)
                result.append('#' + '.' * (m - 1))
    return result

# Example usage:
n, m = 9, 9
snake_pattern = draw_snake(n, m)
for row in snake_pattern:
    print(row)