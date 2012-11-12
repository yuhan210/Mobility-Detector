function [] = selFeaturesAdaboost(train_file, test_file, num_components)
	
	NUM_FEATURE = 8;
	readRawDataFileName = train_file;
	fidRead = fopen(readRawDataFileName, 'r');
	data = textscan(fidRead, '%d %f %f %f %f %f %f %f %f %f', 'delimiter', ',');
	featureVector1=[];
	featureVector1=[ data{2} data{3} data{4} data{5} data{6} data{7} data{9} data{10}];
		
	gt1 = data{1};
	fclose(fidRead);
	
	readTestDataFileName = test_file;
	fidRead = fopen(readTestDataFileName, 'r');
	testData = textscan(fidRead, '%d %f %f %f %f %f %f %f %f %f', 'delimiter', ',');
	featureVector2=[];
	featureVector2=[ testData{2} testData{3} testData{4} testData{5} testData{6} testData{7} testData{9} testData{10}];
	
	gt2 = testData{1};
	fclose(fidRead);
	%Adaboost
 
	trainGT = gt1(1)
	for i = 2 : length(gt1),
		if gt1(i) ~= trainGT,
			testIndex = i
			break
		end
	end
	
	gtVector = ones(length(gt1),1);
	gtVector(testIndex:end,1) = -1;
	[classEstimateClass,modelClass] = adaboost('train', featureVector1, gtVector, 30);
	classFeatureWeight = zeros(NUM_FEATURE,1);
	for i = 1:length(modelClass)
   		 classFeatureWeight(modelClass(i).dimension) = classFeatureWeight(modelClass(i).dimension) + modelClass(i).alpha;
	end	
	%classFeatureWeight	
%	for i = 1:length(modelClass),
%		modelClass(i).error
%	end	
	classFeatureWeight = classFeatureWeight/sum(classFeatureWeight)
	exit;
