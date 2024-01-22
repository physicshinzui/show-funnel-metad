# Visualisation of a Funnel for Funnel Metadynamics


## Usage
In PyMOL,  
```
run draw_funnel.py
showfunnel [plumed input][ligand name(3-letters)]
```

> [!note]
> Each option related to funnel metadynamics in the plumed input file must be in a different row.
> That is, 
> ```
> ZCC=1.8 ALPHA=0.55 
> ```
> raises an error, but 
> ```
> ZCC=1.8
> ALPHA=0.55 
> ```
> works normally.

