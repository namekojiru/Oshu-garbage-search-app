import pickle

with open('fruits_dict.pkl', 'rb') as f:
    a = pickle.load(f)

print(a)