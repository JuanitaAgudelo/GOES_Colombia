# GOES_Colombia

### Para correr la app por primera vez ejecutar: 
  ```sh
  pip install -r requirements.txt
  ```
Despues de instalar las librerias ejecutar:
  ```sh
  chmod +x launch.sh
  ```
Para otorgar los permisos de ejecucion a launch.sh, luego ejecutar los procesos en paralelo 
  ```sh
  ./launch.sh
  ```

### Generación de imágenes satelitales de los productos LST, TPW y radianzas bandas 8,9,10,13,14 al rededor de Colombia

El scrip <em><b> get_cut_compress.py</b></em>, descarga recorta y comprime imagenes satelitales de los productos Land Surface Temperature, Total Precipition Water y Radianzas en las bandas 8,9,10,13,14 del satélite GOES-16 al rededor del territorio Colombiano entre las coordenadas de longitud [-81.03,-64] y latitud [-4.1,12.78]. 

Para ejecutar el scrip desde la terminal de comandos se debe indicar el producto deseado, la fecha de inicio y final de descarga. El producto deseado se agrega pasando el nombre de la función, para radianzas es <em><b>get_Rad</b></em>, para LST es <em><b>get_LST</b></em> y para TPW <em><b>get_TPW</b></em>. La fecha se debe insertar con el formato 'YY-MM-DD-HH:MM'  


## Ejemplo

Queremos descargar imagenes del producto LST entre el año 2020 y 2021. 

  ```sh
  python get_cut_compress.py --func=get_LST --date_ini=2020-01-01-00:00 --date_fin=2021-12-31-23:00 

  ```
