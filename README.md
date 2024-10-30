# lmeca2170-homework
Calculate Delaunay triangulation of the set $P = (\mathbf{x_{0}},\dots,\mathbf{x_{n-1}})$ of n points where $\mathbf{x_{i}} = (x_{i},y_{i})$



Run:
```
python ./src/delaunay.py
```

It explains the program.

---

To generate 10 points of data:
```shell
python genpts.py 10 pts.dat
```
The data looks like this:
```text
10  
0.46700784647740845 0.6826331746074183  
0.801742257215305 0.2618564872995969  
0.5507045110817854 0.6450815283219052  
0.3679930728937706 0.2973935537350594  
0.8520910558865601 0.2641065815199557  
0.3257464690171967 0.04242883432209821  
0.5704843065387448 0.06716582468073617  
0.7788175434708339 0.6305710431331472  
0.7325048474251682 0.044812945678031735  
0.748532776190173 0.19307862118090735
```

---

### Thinking part
```
    def triangulate(self):
        for vertex in self.vertices:
            # What needs to be done here ? 
```

- So we need to one by one add the points, and in each addition re-triangulate
    - This is the main idea of the incremental algorithm we have seen

- There is also the notion of invalid Delaunay triangles when you add a points
    - how is this decided (which primitives are needed here `incircle2d, orient2d`, are these all ?)
    - what are the concrete steps when you find an invalid triangle ?