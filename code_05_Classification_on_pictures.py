#import modules
from utils import *
from vgg16 import Vgg16
from datetime import datetime

#current_dir = os.getcwd()
PROJECT_DIR = 'C:\\Users\\Natalia\\Documents\\GitHub\\Extracting-food-preferences'
CLASSIFICATION_DIR = PROJECT_DIR + '\\classification_with_pics'
PICTURES_DIR       = PROJECT_DIR + '\\pictures\\search_pics'

%cd $CLASSIFICATION_DIR

#Set path to sample/ path if desired
path = CLASSIFICATION_DIR + '\\' + 'sample\\'
#test_path = DATA_HOME_DIR + '/test/' #We use all the test data
results_path=path + 'results\\'
train_path=path + 'train\\'
valid_path=path + 'valid\\'

#import Vgg16 helper class
vgg = Vgg16()

#Set constants. You can experiment with no_of_epochs to improve the model
batch_size=50
no_of_epochs=1

#Finetune the model
batches = vgg.get_batches(train_path, batch_size=batch_size)
val_batches = vgg.get_batches(valid_path, batch_size=batch_size*2)
vgg.finetune(batches)

#Not sure if we set this for all fits
vgg.model.optimizer.lr = 0.01


start = datetime.now()
#Notice we are passing in the validation dataset to the fit() method
#For each epoch we test our model against the validation set
latest_weights_filename = None
for epoch in range(no_of_epochs):
    print("Running epoch: {}".format(epoch))
    vgg.fit(batches, val_batches, nb_epoch=1)
    latest_weights_filename = 'ft{}.h5'.format(epoch)
    vgg.model.save_weights(results_path+latest_weights_filename)
print("Completed {} fit operations".format(no_of_epochs))
end = datetime.now()
total = end - start
print('Time to run the script on CPU is {}'.format(total))