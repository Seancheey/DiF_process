M = csvread('DiF/points/0000001.pts');
X = M(:,1)
Y = M(:,2)
figure;
img = imread('DiF/cropped/0000001-00.jpg');
figure
imshow(img);
hold on;
plot(X,Y,'r+','MarkerSize',10)
uiwait(msgbox('Locate the point'));

