#/usr/bin/env python3

from pprint import pprint
from pyscipopt import Model

# Preferred output values for tumor categories
BENIGN = 1
MALIGNANT = -1

def read_proben1_cancer_data(filename, train_size):
    '''Loads a proben1 cancer file into train & test sets'''
    # Number of input data points per record
    DATA_POINTS = 9

    train_data = []
    test_data = []

    with open(filename) as infile:
        # Read in the first train_size lines to a training data list, and the
        # others to testing data. This allows us to test how general our model
        # is on something other than the input data.
        for line in infile.readlines()[7:]: # skip header
            line = line.split()

            # Records = offset (x0) + remaining data points
            input = [float(x) for x in line[:DATA_POINTS]]
            output = BENIGN if line[-2] == '1' else MALIGNANT
            record = {'input': input, 'output': output}

            # Determine what data set to put this in
            if len(train_data) >= train_size:
                test_data.append(record)
            else:
                train_data.append(record)

    return train_data, test_data

def train_linear_model(train_data):
    '''
    Accepts a set of input training data with known output
    values.  Returns a list of coefficients to apply to
    arbitrary records for purposes of binary categorization.
    '''
    # Make sure we have at least one training record.
    assert len(train_data) > 0
    num_variables = len(train_data[0]['input'])

    # Variables are coefficients in front of the data points. It is important
    # that these be unrestricted in sign so they can take negative values.
    m = Model()
    x = [m.addVar(f'x{i}', lb=None) for i in range(num_variables)]

    # Residual for each data row
    residuals = [m.addVar(lb=None, ub=None) for _ in train_data]
    for r, d in zip(residuals, train_data):
        # r will be the absolute value of the difference between observed and
        # predicted values. We can model absolute values such as r >= |foo| as:
        #
        #   r >=  foo
        #   r >= -foo
        m.addCons(sum(x * y for x, y in zip(x, d['input'])) + r >= d['output'])
        m.addCons(sum(x * y for x, y in zip(x, d['input'])) - r <= d['output'])

    # Find and return coefficients that min sum of residuals.
    m.setObjective(sum(residuals))
    m.setMinimize()
    m.optimize()

    solution = m.getBestSol()
    return [solution[xi] for xi in x]

def count_correct(data_set, coefficients):
    '''Returns the number of correct predictions.'''
    correct = 0
    for d in data_set:
        result = sum(x*y for x, y in zip(coefficients, d['input']))

        # Do we predict the same as the output?
        if (result >= 0) == (d['output'] >= 0):
            correct += 1

    return correct

if __name__ == '__main__':
    # Specs for this input file
    INPUT_FILE_NAME = 'cancer1.dt'
    TRAIN_SIZE = 350

    train_data, test_data = read_proben1_cancer_data(
        INPUT_FILE_NAME,
        TRAIN_SIZE
    )

    # Add the offset variable to each of our data records
    for data_set in [train_data, test_data]:
        for row in data_set:
            row['input'] = [1] + row['input']

    coefficients = train_linear_model(train_data)
    print('coefficients:')
    pprint(coefficients)

    # Print % of correct predictions for each data set
    correct = count_correct(train_data, coefficients)
    print(
        '%s / %s = %.02f%% correct on training set' % (
            correct, len(train_data),
            100 * float(correct) / len(train_data)
        )
    )

    correct = count_correct(test_data, coefficients)
    print(
        '%s / %s = %.02f%% correct on testing set' % (
            correct, len(test_data),
            100 * float(correct) / len(test_data)
        )
    )
