clear;
%%

readRawDataFileName = 'train_1';
fidRead = fopen(readRawDataFileName, 'r');
data = textscan(fidRead, '%f %f %d', 'delimiter', ',');
featureVector1 = [data{1} data{2}] ;
gt1 = data{3};
fclose(fidRead);

readTestDataFileName = 'test_1';
fidRead = fopen(readTestDataFileName, 'r');
testData = textscan(fidRead, '%f %f %d', 'delimiter', ',');
featureVector2 = [testData{1} testData{2}];
gt2 = testData{3};
fclose(fidRead);

%%
%Decision Tree%
%t = ClassificationTree.fit(featureVector1,gt1,'CategoricalPredictors', 'all')
t = classregtree(featureVector1,gt1,'method','classification');

DTpredcitedLabel2Cell = eval(t,featureVector2);
for i = 1 : length(DTpredcitedLabel2Cell),
    DTpredcitedLabel2(i,1) = int32(str2num(DTpredcitedLabel2Cell{i}));
end
cMat1 = confusionmat(gt2,DTpredcitedLabel2);
disp('Decision Tree - 1')
for i = 1: 5,
   accuracy(i) = cMat1(i,i)/sum(cMat1(i,1:end));
end

clear t;

t = classregtree(featureVector2,gt2,'method','classification');
DTpredcitedLabel1Cell = eval(t,featureVector1);
for i = 1 : length(DTpredcitedLabel1Cell),
    DTpredcitedLabel1(i,1) = int32(str2num(DTpredcitedLabel1Cell{i}));
end
cMat2 = confusionmat(gt1,DTpredcitedLabel1)
disp('Decision Tree - 2')
for i = 1: 5,
   accuracy2(i) = cMat2(i,i)/sum(cMat2(i,1:end));
end
disp('Decision Tree - total')
decisionTreeAccuracy = (accuracy + accuracy2)/2
clear t;

%%
%Naive Bayes%
BaysianObject = NaiveBayes.fit(featureVector1,gt1,'Prior','uniform'); %classLabel=  posterior(BaysianObject,testVector)
classLabel=  BaysianObject.predict(featureVector2);
cMat1 = confusionmat(gt2,classLabel);


for i = 1: 5,
   accuracy(i) = cMat1(i,i)/sum(cMat1(i,1:end));
end
disp('Naive Bayes - 1')
accuracy

clear BaysianObject;

BaysianObject=NaiveBayes.fit(featureVector2,gt2,'Prior','uniform');
classLabel=  BaysianObject.predict(featureVector1);
cMat2 = confusionmat(gt1,classLabel);

for i = 1: 5,
   accuracy2(i) = cMat2(i,i)/sum(cMat2(i,1:end));
end
disp('Naive Bayes - 2')
accuracy2
disp('Naive Bayes total')
NaiveBayesAccuracy = (accuracy + accuracy2)/2

