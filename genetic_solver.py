from PIL import Image
import numpy as np
import pandas as pd
import os
from argparse import ArgumentParser

# Parse command line arguments
parser = ArgumentParser()
# Arguments related to the genetic optimization
parser.add_argument('--population_size', type=int, default=100, help='Number of solutions in the population')
parser.add_argument('--max_generations', type=int, default=32, help='Number of generations to run the genetic optimization')
parser.add_argument('--mutation_rate', type=float, default=10, help='Rate of mutation when creating offspring solutions')
parser.add_argument('--overlap_regulation', type=float, default=50, help='Regulation factor for the overlap between fragments (used in the fitness function)')
parser.add_argument('--early_stop', type=int, default=16, help='Number of generations (without improvement) to wait before early stopping')
# Arguments related to the image processing
parser.add_argument('--resize', type=int, default=100, help='Size of the fragments in the puzzle (smaller values will speed up the optimization)')
parser.add_argument('--canvas_size', type=int, default=1000, help='Size of the canvas to place the fragments on (should be large enough to fit all fragments)')
# Arguments related to the input/output
parser.add_argument('--input_dir', type=str, default='puzzle', help='Path to a directory containing the fragments of the puzzle')
parser.add_argument('--output_solution', type=str, default='solution.csv', help='Path to save the CSV file with the solution to the puzzle')
parser.add_argument('--output_image', type=str, default='solution.png', help='Path to save the image of the solution')
parser.add_argument('--verbose', action='store_true', help='Whether to print the fitness loss at each generation')

args = parser.parse_args()


def init_population(population_size, n_fragments):
    """
    Initializes the population with random soluitons

    Args:
    -----
    `population_size` : int
        Number of solutions in the population

    `n_fragments` : int
        Number of fragments in the puzzle

    Returns:
    --------
    `population` : np.ndarray
        Population of solutions with shape (population_size, n_fragments, 3) where the last dimension represents the x, y, and rotation of each fragment
    """
    population = np.zeros((population_size, n_fragments, 3))
    population[:, :, :2] = np.random.randint(args.canvas_size // 4, 3 * args.canvas_size // 4, (population_size, n_fragments, 2))
    population[:, :, 2] = np.random.ranf((population_size, n_fragments)) * 360
    return population

import matplotlib.pyplot as plt
def get_solution_image(puzzle, solution, canvas_size=args.canvas_size, get_overlap=False):
    """
    Creates an image, depicting the given solution to the puzzle

    Args:
    -----
    `puzzle` : list(PIL.Image)
        List of images, each representing a fragment of the puzzle

    `solution` : np.ndarray
        The solution to the puzzle, shape (n_fragments, 3) where the last dimension represents the x, y, and rotation of each fragment

    `get_overlap` : bool
        Whether to return the overlap - the number of pixels that are covered by more than one fragment (default: False)

    Returns:
    --------
    `image` : PIL.Image
        An image representing the solution to the puzzle

    `overlap` : int
        The number of pixels that are covered by more than one fragment
    """
    image = np.zeros((canvas_size, canvas_size, 4))
    # Paste each fragment onto the canvas according to the solution
    for frag, config in zip(puzzle, solution):
        frag_rot = frag.rotate(config[2])
        frag_height, frag_width = frag_rot.size
        x_offset, y_offset = np.round(config[:2]).astype(int)
        y_offset, x_offset = y_offset - frag_height // 2, x_offset - frag_width // 2
        canvas = Image.new('RGBA', (canvas_size, canvas_size), (0, 0, 0, 0))
        canvas.paste(frag_rot, (y_offset, x_offset), mask=frag_rot)
        image += np.array(canvas)
    # plt.imshow(image[:, :, 3])
    # plt.show()
    overlap = np.sum(image[:, :, 3] > 255) # Number of pixels that are covered by more than one fragment
    image = Image.fromarray(image.astype(np.uint8))
    return (image, overlap) if get_overlap else image


def fitness_loss(puzzle, solution):
    """
    Computes the fitness loss of a solution to the puzzle

    Args:
    -----
    `puzzle` : list(PIL.Image)
        List of images, each representing a fragment of the puzzle

    `solution` : np.ndarray
        The solution to the puzzle, shape (n_fragments, 3) where the last dimension represents the x, y, and rotation of each fragment

    Returns:
    --------
    `fitness_loss` : float
        The fitness loss (opposite of traditional "fitness" in genetic programming) of the solution
    """
    image, overlap = get_solution_image(puzzle, solution, get_overlap=True)
    bbox = image.getbbox() # Get the bounding box of the image
    if bbox is None: # To handle edge cases, if the image is empty, the fitness loss is infinate
        return float('inf')
    # The fitness loss is the area of the bounding box plus the overlap between fragments (multiplied by a regulation factor)
    # The regulation factor is used to balance the importance of the the overlap
    return (bbox[2] - bbox[0]) * (bbox[3] - bbox[1]) + overlap * args.overlap_regulation


def crossover(parents, mutation_rate=1):
    """
    Creates an offspring from a pair of parents

    Args:
    -----
    `parents` : np.ndarray
        The parents of the offspring (two solutions), shape (2, n_fragments, 3) where the last dimension represents the x, y, and rotation of each fragment

    `mutation_rate` : float
        The rate of mutation (default: 1)

    Returns:
    --------
    `offspring` : np.ndarray
        The offspring of the parents, shape (n_fragments, 3) where the last dimension represents the x, y, and rotation of each fragment
    """
    # The offspring is the average of the parents plus some noise
    return np.average(parents, axis=0) + np.random.normal(0, mutation_rate, parents[0].shape)


def genetic_puzzle_solver(puzzle, population_size, max_generations, mutation_rate):
    """
    A genetic programming approach to solve unrestricted jigsaw puzzles

    Args:
    -----
    `puzzle` : list(PIL.Image)
        List of images, each representing a fragment of the puzzle

    `population_size` : int
        Number of solutions in the population

    `max_generations` : int
        Number of generations to run the genetic optimization

    `mutation_rate` : float
        Rate of mutation when creating offspring solutions

    Returns:
    --------
    `solution` : np.ndarray
        The solution to the puzzle, shape (n_fragments, 3) where the last dimension represents the x, y, and rotation of each fragment
    """
    # Initialize the population and compute the fitness loss of each individual
    population = init_population(population_size, len(puzzle))
    fitness_losses = [fitness_loss(puzzle, solution) for solution in population]
    early_stop = {'count': 0, 'last_loss': 0} # Initialize the early stopping mechanism
    for generation in range(max_generations):
        fitness_ranks = np.argsort(fitness_losses)
        # Replace the worst 25% of the population with offspring from the best 50% of the population
        for i in range(population_size // 4):
            parents = population[fitness_ranks[2*i:2*(i+1)]]
            offspring = crossover(parents, mutation_rate)
            population[fitness_ranks[-(i+1)]] = offspring
            fitness_losses[fitness_ranks[-(i+1)]] = fitness_loss(puzzle, offspring)
        if args.verbose:
            print(f'Generation {generation + 1}/{max_generations}, fitness-loss: {fitness_losses[fitness_ranks[0]]}')
        # Update and check the early stopping mechanism
        if fitness_losses[fitness_ranks[0]] == early_stop['last_loss']:
            early_stop['count'] += 1
        else:
            early_stop['count'] = 0
            early_stop['last_loss'] = fitness_losses[fitness_ranks[0]]
        if early_stop['count'] > 16:
            break
    # Return the best solution found in the last generation
    return population[fitness_ranks[0]]

if __name__ == '__main__':
    # Load the fragments of the puzzle from the input directory
    filenames = os.listdir(args.input_dir)
    puzzle = [Image.open(os.path.join(args.input_dir, file)).convert('RGBA') for file in filenames]
    # Resize the fragments to the desired size
    puzzle_resized = [frag.resize((args.resize, args.resize)) for frag in puzzle]
    # Solve the puzzle using genetic optimization
    solution = genetic_puzzle_solver(puzzle_resized, args.population_size, args.max_generations, args.mutation_rate)
    # Transform the solution to the original size of the fragments
    original_size = max(puzzle[0].size)
    solution[:, :2] = np.round(solution[:, :2]).astype(int) * (original_size / args.resize)
    # Modulo 360 to keep the rotation within the range [0, 360)
    solution[:, 2] = solution[:, 2] % 360
    # Save the solution to a CSV file
    solution_df = pd.DataFrame(solution, columns=['x', 'y', 'rot'])
    solution_df.insert(0, 'rpf', filenames)
    solution_df.to_csv(args.output_solution, index=False)
    # Save the image of the solution
    image = get_solution_image(puzzle, solution, canvas_size=original_size*10)
    image.save(args.output_image)
    print(f'Solution saved to {args.output_solution} and {args.output_image}')

