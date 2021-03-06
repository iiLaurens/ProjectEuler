"""

Grid Zero

=========

You are almost there. The only thing between you and foiling Professor Boolean's
plans for good is a square grid of lights, only some of which seem to be lit up.

The grid seems to be a lock of some kind. That's interesting. Touching a light
toggles the light, as well as all of the other lights in the same row and column
as that light.

Wait! The minions are coming - better hide.

Yes! By observing the minions, you see that the light grid is, indeed, a lock.
The key is to turn off all the lights by touching some of them. The minions are
gone now, but the grid of lights is now lit up differently. Better unlock it
fast, before you get caught.

The grid is always a square. You can think of the grid as an NxN matrix of
zeroes and ones, where one denotes that the light is on, and zero means that the
light is off.

For example, if the matrix was

1 1
0 0

Touching the bottom left light results in

0 1
1 1

Now touching the bottom right light results in

0 0
0 0

...which unlocks the door.


Write a function answer(matrix) which returns the minimum number of lights that
need to be touched to unlock the lock, by turning off all the lights. If it is
not possible to do so, return -1.

The given matrix will be a list of N lists, each with N elements.
Element matrix[i][j] represents the element in row i, column j of the matrix.

Each element will be either 0 or 1, 0 representing a light that is off, and 1
representing a light that is on.

N will be a positive integer, at least 2 and no more than 15.
"""
# Variant using bit operations
from itertools import chain, combinations, product, starmap
from operator import xor

def answer(matrix):
    # This solution uses linear algebra (who ever thought I would find use
    # for it again after college) to find the answer. For this to work, note
    # that the initial condition of each light is the result of starting from
    # an empty grid (all lights off) and pressing buttons. This results in
    # a system of equations which can be used to solve the problem.
    
    
    # First we 'define' a variable to each initial light condition (on = 1,
    # off = 0). Create a similar variable for the switch on each position that
    # is required to obtain the initial state of lights (value 1 = switch is
    # used, 0 = switch not used). Note that a switch only takes two values since
    # pressing a switch twice has no net effect to the state of the board. 
    # This suggests that we can apply a modulo 2 field to all our operations as well.
    
    # Now for every light variable, the initial value of the light is equal to the sum
    # of switches pressed in that column and row (and then modulo 2). This results
    # in a system of equations that has a matrix representation as seen in the matrix M below.
    # If the length of the board is even, this matrix is invertible and a single solution
    # exists (with the modulo 2 field applied). Luckily, the inverted matrix equals itself
    # so the solution is obtained by simply multiplying M with the initial state to obtain
    # which switches need to be pressed, and summing the resulting vector.
    
    # For a board with odd length, the matrix is non-invertible and no single solution
    # exists. The trick is to augment the board with an extra row and column to make
    # the board length even again. However, our solution can then include switches only
    # included on the augmented board. Restricting these switch variables from turning 1
    # is the key to success.
      
    t = len(matrix)
    s = t + 1 if t % 2 == 1 else t

    # Create (augmented) system of equations
    M = [[1 if (j % s) == (i % s) or (j // s) == (i // s) else 0 for j in range(s*s)] for i in range(s*s)]
    flatInitial = matrix2list(matrix)
    
    if s != t:
        # For reasoning it is convenient to group the variables belonging to the augmented
        # row/column together and have them be the last set of equations/variables.
        # Note that we are deciding the switches required as a function of the initial state
        # and initial state as a function of switches simultanously (which is is possible
        # because the augmented matrix is invertible and the inverse equals itself).
        for j in range(2):
            M = transpose(M)
            for i in range(s*s - 1, -1, -s):
                    M.append(M.pop(i))
                    
        # Example of matrix for (augmented) 4x4 matrix
        #                    cols   rows
        #                   ~~~~~~~~~~~~~ Augmented light variables (can be varied)
        # 1 1 1 1 . . 1 . . 1 . . . . . 1 
        # 1 1 1 . 1 . . 1 . . 1 . . . . 1 
        # 1 1 1 . . 1 . . 1 . . 1 . . . 1 
        # 1 . . 1 1 1 1 . . 1 . . . . 1 . 
        # . 1 . 1 1 1 . 1 . . 1 . . . 1 . 
        # . . 1 1 1 1 . . 1 . . 1 . . 1 . 
        # 1 . . 1 . . 1 1 1 1 . . . 1 . . 
        # . 1 . . 1 . 1 1 1 . 1 . . 1 . . 
        # . . 1 . . 1 1 1 1 . . 1 . 1 . . 
        # 1 . . 1 . . 1 . . 1 1 1 1 . . .  |
        # . 1 . . 1 . . 1 . 1 1 1 1 . . .  |
        # . . 1 . . 1 . . 1 1 1 1 1 . . .  |
        # . . . . . . . . . 1 1 1 1 1 1 1  |  Augmented switch conditions
        # . . . . . . 1 1 1 . . . 1 1 1 1  |  (must be zero)
        # . . . 1 1 1 . . . . . . 1 1 1 1  |
        # 1 1 1 . . . . . . . . . 1 1 1 1  |
        
        # Split the matrix into 4 regions. Equations (rows) at the top belong to
        # 'real' variables and at the bottom correspond to 'augmented' variables.
        # The same division holds for each sum component (left vs right).
        
        # For performance, interpret vectors with 0 and 1's as bits and save the corresponding int.
        # In this way we can use much more efficient bit operations to 'flip' vectors.

        M_top_left =    [row[:t*t] for row in M[:t*t]]
        M_top_right =   [row[t*t:] for row in M[:t*t]]
        M_down_left =   [row[:t*t] for row in M[t*t:]] # same as transpose(M_top_right)
        # M_down_right = [row[t*t:] for row in M[t*t:]]
        
        # Precalculate some parts of the matrix multiplication with information we
        # we know cannot change (since they depend on the initial state).
        V_top_left = mmult(M_top_left, flatInitial)
        V_down_left = mmult(M_down_left, flatInitial)
        
        # For performance, interpret vectors with 0 and 1's as bits and save the corresponding int.
        # In this way we can use much more efficient bit operations to 'flip' vectors.
        int_top_left = bitlist2int(V_top_left)
        int_top_right = [bitlist2int(V) for V in M_down_left]
        
        for i in int_top_right[:t]:
            print format(i, "025b")
        
    
        set_a, set_b = (set(V_down_left[:t]), set(V_down_left[t+1:]))

        # Looking at the last rows of M, we can observe two conditions:
        # If the switches of the augmented variables cannot be pressed,
        # then the sum of initial lights as represented by the last rows of M
        # must equate to0. Two conditions can be derived: set_a variables must
        # be the same andset_b variables must be the same. Also, set_a
        # variables must be the same to set_b variables for the middle equation
        # to result in 0.
        if set_b == set_a and len(set_a) == 1:
            
            # Now we can choose our 'augmented' light variables but we must
            # consider that the sum of that row equals 0. For every option,
            # we save the would-be solution and return the best one.
            
            min_solution = bin(int_top_left).count("1") # Every 1 represents a switch that must be pressed
            for option_col in combinations_augmented_col(int_top_right[:t], 1):
                # Calculate partial solution
                solution = best_augmented_row(int_top_left ^ option_col, int_top_right[t+1:], 1)
                min_solution = min(min_solution, solution)
            return min_solution
        else:
            # The last 2*t+1 equations in matrix M are invalid, so no solution possible
            return -1
    else:
        # Even size grid. Simply solve matrix multiplication.
        return sum(mmult(M, flatInitial))
    
def mmult(X,y):
    # Multiplies matrix with vector
    return [sum([a*b for a,b in zip(X[i], y)])%2 for i in range(len(X))]

def matrix2list(M):
    return [M[i][j] for i, j in product(range(len(M)), range(len(M)))]

def combinations_augmented_col(lst, modulo):
    # Iterates all combinations of on-lights in the augmented columns in such a way that
    # there is a even (modulo = 0) or uneven (modulo = 1) amount of lights chosen.
    # Also, the effect on on the original switch variables is precomputed by means of
    # xor operation
    return (reduce(xor, i, 0) for i in chain(*(combinations(lst, r) for r in range(modulo,len(lst)+1,2))))

def best_augmented_row(partial_solution, lst, modulo):
    # This function greedily reduces the 1's in the given solution
    # by turning augmented row lights on. First assume no lights are on.
    t = len(lst)
    option_row = []
    
    print(t)
    
    # for each augmented row light
    for i in range(t):
        # If already more 1's than 0's in a row in the given partial solution
        # then the solution benefits by having the augmented row light on
        if format(partial_solution, "0" + str(t*t) + "b")[i*t: (i+1)*t].count("1") > t / 2.0:
            option_row.append(lst[t - i - 1])
    
    if len(option_row) % 2 == modulo:
        # Modulo happens to be correct already, so return current value
        return bin(partial_solution ^ reduce(xor, option_row, 0)).count("1")
    else:
        # Modulo not correct, so remove one from the set to correct the modulo
        # or add one to the set in the exceptional case that the modulo is 1
        # and the set is empty.
        combinationset = combinations(option_row, len(option_row) - 1) if not (modulo == 1 and len(option_row) == 0) else [[i] for i in lst]
        
        best_count = t*t
        for subset in combinationset:
            tmp = partial_solution ^ reduce(xor, subset, 0)
            best_count = min(bin(tmp).count("1"), best_count)
        return best_count
                
    

def transpose(M):
    return [[row[i] for row in M] for i in range(len(M))]

def bitlist2int(bitlist):
    out = 0
    for bit in bitlist:
        out = (out << 1) | bit
    return out
