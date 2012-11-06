clear;
%%

readRawDataFileName = 'train';
fidRead = fopen(readRawDataFileName, 'r');
data = textscan(fidRead, '%f %f %f %f %f %f %f %f %f %d', 'delimiter', ',');
featureVector1 = [data{1} data{2} data{3} data{4} data{5} data{6} data{7} data{8} data{9}];
%featureVector1 = [ data{1} data{2} data{3} ] ;
gt1 = data{10};
fclose(fidRead);

readTestDataFileName = 'test';
fidRead = fopen(readTestDataFileName, 'r');
testData = textscan(fidRead, '%f %f %f %f %f %f %f %f %f %d', 'delimiter', ',');
featureVector2 = [testData{1} testData{2} testData{3} testData{4} testData{5} testData{6} testData{7} testData{8} testData{9}] ;
%featureVector2 = [ testData{1} testData{2} testData{3} ] ;
gt2 = testData{10};
fclose(fidRead);

%%
%Decision Tree%
%t = ClassificationTree.fit(featureVector1,gt1,'CategoricalPredictors', 'all')
t = classregtree(featureVector1,gt1,'method','classification');

DTpredcitedLabel2Cell = eval(t,featureVector2);
for i = 1 : length(DTpredcitedLabel2Cell),
    DTpredcitedLabel2(i,1) = int32(str2num(DTpredcitedLabel2Cell{i}));
end
cMat1 = confusionmat(gt2,DTpredcitedLabel2,'ORDER',[0 1 2 3 4])
disp('Decision Tree - 1')
for i = 1: size(cMat1,1),
   accuracy(i) = cMat1(i,i)/sum(cMat1(i,1:end));
end

clear t;

t = classregtree(featureVector2,gt2,'method','classification');
DTpredcitedLabel1Cell = eval(t,featureVector1);
for i = 1 : length(DTpredcitedLabel1Cell),
    DTpredcitedLabel1(i,1) = int32(str2num(DTpredcitedLabel1Cell{i}));
end
cMat2 = confusionmat(gt1,DTpredcitedLabel1,'ORDER',[0 1 2 3 4])
disp('Decision Tree - 2')
for i = 1: size(cMat2,1),
   accuracy2(i) = cMat2(i,i)/sum(cMat2(i,1:end));
end
disp('Decision Tree - total')
decisionTreeAccuracy = (accuracy + accuracy2)/2
clear t;

%%
%Naive Bayes%
BaysianObject = NaiveBayes.fit(featureVector1,gt1,'Prior','uniform'); %classLabel=  posterior(BaysianObject,testVector)
classLabel=  BaysianObject.predict(featureVector2);
cMat1 = confusionmat(gt2,classLabel)


for i = 1: size(cMat1,1),
   accuracy(i) = cMat1(i,i)/sum(cMat1(i,1:end));
end
disp('Naive Bayes - 1')
accuracy

clear BaysianObject;

BaysianObject=NaiveBayes.fit(featureVector2,gt2,'Prior','uniform');
classLabel=  BaysianObject.predict(featureVector1);
cMat2 = confusionmat(gt1,classLabel)

for i = 1: size(cMat2,1),
   accuracy2(i) = cMat2(i,i)/sum(cMat2(i,1:end));
end
disp('Naive Bayes - 2')
accuracy2
disp('Naive Bayes total')
NaiveBayesAccuracy = (accuracy + accuracy2)/2

