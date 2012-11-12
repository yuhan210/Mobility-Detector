%%
function [] = classification(train_file,test_file,num_components)
	readRawDataFileName = train_file;
	fidRead = fopen(readRawDataFileName, 'r');
	data = textscan(fidRead, '%d %f %f %f %f %f %f %f %f %f', 'delimiter', ',');
	featureVector1=[];
	%for i = 1:num_components,
        %   featureVector1 = [featureVector1 data{i+1}];
        %end
	featureVector1 = [data{4}];
	gt1 = data{1};
	fclose(fidRead);
	
	readTestDataFileName = test_file;
	fidRead = fopen(readTestDataFileName, 'r');
	testData = textscan(fidRead, '%d %f %f %f %f %f %f %f %f %f', 'delimiter', ',');
	featureVector2=[];
	%for i = 1:num_components,
        %   featureVector2 = [featureVector2 testData{i+1}];
        %end
	featureVector2 = [testData{4}];
	gt2 = testData{1};
	fclose(fidRead);
	
	%%
	%Decision Tree%
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
	accuracy
	clear t;
		
	%%
	%Naive Bayes%
	BaysianObject = NaiveBayes.fit(featureVector1,gt1,'Prior','uniform'); %classLabel=  posterior(BaysianObject,testVector)
	classLabel=  BaysianObject.predict(featureVector2);
	cMat1 = confusionmat(gt2,classLabel,'ORDER',[0 1 2 3 4])
	
	for i = 1: size(cMat1,1),
	   accuracy(i) = cMat1(i,i)/sum(cMat1(i,1:end));
	end
	disp('Naive Bayes - 1')
	accuracy	
	

	%%
	%Adaboost
 	%{
	[estimateClass, modelClass] = adaboost('train',featureVector1, gt1, 100);
	classFeatureWeight = zeros(NUM_FEATURE,1);
	for i = 1:length(modelClass)
   		 class0FeatureWeight(modelClass(i).dimension) = class0FeatureWeight(modelClass(i).dimension) + modelClass(i).alpha;
	end	
	%}
	exit;
