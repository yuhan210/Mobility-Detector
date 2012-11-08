%%
function [] = classification(train_file,test_file)
	readRawDataFileName = train_file;
	fidRead = fopen(readRawDataFileName, 'r');
	data = textscan(fidRead, '%d %f %f %f %f %f %f %f %f %f', 'delimiter', ',');
	featureVector1 = [data{2} data{3} data{4} data{5} data{6} data{7} data{8} data{9}];
	gt1 = data{1};
	fclose(fidRead);
	
	readTestDataFileName = test_file;
	fidRead = fopen(readTestDataFileName, 'r');
	testData = textscan(fidRead, '%d %f %f %f %f %f %f %f %f %f', 'delimiter', ',');
	featureVector2 = [testData{2} testData{3} testData{4} testData{5} testData{6} testData{7} testData{8} testData{9}] ;
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
	exit;
