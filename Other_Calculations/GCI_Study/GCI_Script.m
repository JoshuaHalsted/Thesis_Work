clc, clear all

%This code uses the Fixed-Point Iteration method to determine the

%grid convergence index:

%Establishing characteristic cell size:

V=0.359392; %computational domain volume in m^3

Cells1=17561115; %Number of cells in fine mesh

Cells2=12864691; %Number of cells in medium mesh

Cells3=8606941; %Number of cells in coarse mesh

h1=(V/Cells1)^(1/3); %Fine mesh characteristic size

h2=(V/Cells2)^(1/3); %Medium mesh characteristic size

h3=(V/Cells3)^(1/3); %Coarse mesh characteristic size

%Read the Excel Spreadsheet data

filename='Mesh_sens4.xlsx';

data=xlsread(filename);

X=data(:,1); %X line integral array

Phi1=data(:,2); %Fine mesh solution

Phi2=data(:,3); %Medium mesh solution

Phi3=data(:,4); %Coarse mesh solution

%Global Constants:

l=length(Phi1); %Number of points in the solution vector

r21=h2/h1; %Ratio between medium and fine mesh sizes (h2/h1)

r32=h3/h2; %Ratio between coarse and medium mesh sizes (h3/h2)

r31=h3/h1; %Ratio between coarse and fine mesh sizes (h3/h1)

display('The mesh size refinement factors are:')

if r31>1.3

display('The refinement factor r=h_coarse/h_fine is greater than 1.3')

else

display('The refinement factor r=h_coarse/h_fine is unsatisfactory.')

end

if r21>1.3 && r32>1.3

display('The refinement factors r21 and r32 are both greater than 1.3')

else

display('The refinement r21 and r32 factors are unsatisfactory.')

end

eps21=Phi2-Phi1; %Difference in solutions between medium and fine meshes

eps32=Phi3-Phi2; %Difference in solutions between coarse and medium meshes

s=1*sign(eps32./eps21); %Sign of the ratio of solution differences

Oscil=0; %Start oscillatory convergence point

%counter

for i=1:l

if s(i)<0

Oscil=Oscil+1;

end

end

NormOscil=100*(Oscil/l); %Normalized number of data points

Mono=l-Oscil; %Monotonic convergence point counter;

NormMono=100*(Mono/l); %Normalized number of data point

%Display the number of oscillatory convergence points:

fprintf('\n')

fprintf('Convergence type:')

fprintf('\n')

fprintf('Number of points with Monotonic Convergence: %d\n',Mono)

fprintf('Percent occurence of Monotonic Convergence:%.2f%%\n',NormMono)

fprintf('\n')

fprintf('Number of points with Oscillatory Convergence: %d\n',Oscil)

fprintf('Percent occurence of Oscillatory Convergence:%.2f%%\n',NormOscil)

fprintf('\n')

%Vector Initialization and First Guesses:

Initial_Guess=2; %Initial guess for global order of accuracy

p=Initial_Guess; %Setting local order of accuracy guess

q=zeros(l,1);

%q(:,1)=log((r21^p-s)./(r32^p-s)); %Initial guess for q(p) input

err=1; %Initial error

%Applying the Fixed-Point Iteration method:

tol=1e-5; %Residual tolerance

iter=1; %Start iteration counter

i=1; %First vector component

while i<l+1

 

p(iter+1)=(1/log(r21))*abs(log(abs(eps32(i)/eps21(i)))+q(i,iter));

q(i,iter+1)=log((r21^p(iter+1)-s(i))/(r32^p(iter+1)-s(i)));

 

 err=p(iter+1)-p(iter); %Establish current iteration error

 

 if abs(err)>=tol %Verify error is above tolerance

iter=iter+1;

else

P(i)=p(iter); %Record final iteration of "p"

Iter(i)=iter; %Record number of iterations

p=Initial_Guess; %Reinitialize guess

iter=1; %Reinitialize iteration counter

i=i+1; %Proceed to next component in vector

end

 

 if i>=l+1; %Check to see if all vector components are complete

break

end

end

%Reorient values:

P=P';

Iter=Iter';

MeanP=mean(P); %Average Global Order of Accuracy

fprintf('Average Apparent Order: p=%2.2f\n',MeanP)

%Extrapolated values are:

Phiext21=(r21.^MeanP.*Phi1-Phi2)./(r21.^MeanP-1);

Phiext32=(r32.^MeanP.*Phi2-Phi3)./(r32.^MeanP-1);

%Extrapolated relative error is:

Errext21=abs((Phiext21-Phi1)./Phiext21).*100;

Errext32=abs((Phiext32-Phi2)./Phiext32).*100;

%Approximate relative error is:

Erra_21=abs((Phi1-Phi2)./Phi1).*100;

Erra_32=abs((Phi2-Phi3)./Phi2).*100;

%GCI is:

GCI21=(1.25.*Erra_21)./(r21.^P-1);

GCI32=(1.25.*Erra_32)./(r32.^P-1);

%GCI with averaged global order of accuracy:

A_GCI21=(1.25.*Erra_21)./(r21.^MeanP-1);

A_GCI32=(1.25.*Erra_32)./(r32.^MeanP-1);

%Adjusted GCIs from percentages

Error21=(A_GCI21.*Phi1)/100;

Error32=(A_GCI32.*Phi2)/100;

%Convergence?

Converge=(GCI32)./((r21.^(P)).*GCI21);

A_Converge=(GCI32)./((r21.^(MeanP)).*GCI21);

%Plot fine solution results with uncertainty bars:

figure

plot(X,Phi1,X,Phi1+Error21,'r--',X,Phi1-Error21,'r--')

ylabel('Velocity [m/s]','Fontsize',22)

xlabel('X [m]','Fontsize',22)

title('Line Probe velocity, Fine Mesh','Fontsize',22)

leg1=legend('Fine Solution','Uncertainty Bands');

set(leg1,'Fontsize',18)

figure

plot(X,Phi2,'o',X,Phi2+Error32,'r:',X,Phi2-Error32,'r:');

ylabel('Velocity [m/s]','Fontsize',22)

xlabel('X [m]','Fontsize',22)

title('Line Probe velocity, Medium Mesh','Fontsize',22)

figure

plot(X,Phi3,'x',X,Phi2,'o',X,Phi1,'+')

hold on

plot1= plot(X,Phiext21,'black')

set(plot1,'LineWidth',2.5)

leg2=legend('Coarse Solution','Medium Solution','Fine Solution','Extrapolated Solution','Fontsize',18);

set(leg2,'Fontsize',18)

ylabel('Velocity [m/s]','Fontsize',22)

xlabel('X [m]','Fontsize',22)

title('Line Probe velocity, Coarse Mesh','Fontsize',22)

%Plot errors:

figure

plot(X,Errext21,'-+',X,Errext32,'-x')

leg3=legend('Medium-Fine Meshes','Coarse-Medium Meshes');

set(leg3,'Fontsize',18)

xlabel('X (s)','Fontsize',22)

ylabel('Extrapolated Error (%)','Fontsize',22)

title('Line Probe velocity Extrapolated Error versus X','Fontsize',22)

figure

plot(X,Erra_21,'-x',X,Errext32,'-x')

xlabel('X (s)','Fontsize',22)

ylabel('Relative Error (%)','Fontsize',22)

title('Line Probe velocity, Medium Mesh Relative Error versus X','Fontsize',22)

leg4=legend('Medium-Fine Meshes','Coarse-Medium Meshes');

set(leg4,'Fontsize',18)