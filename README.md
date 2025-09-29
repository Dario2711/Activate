# Activate
## COMANDOS PARA TRABAJAR EN ESTE REPO
- `git clone https://github.com/Dario2711/Activate`: Clona el repo, si no tenes en local
- `git checkout develop`: Te posiciona en la rama develop
- `git pull origin develop`: Trae los cambios del repo remoto al local en caso de q este ultimo este desactualizado (si no usaste clone)
- `git checkout -b (nombre de la rama)`: Crea una rama y te posiciona en la misma
- **Todas las ramas heredan el codigo de develop ya que este es el q debe estar mas actualizado**

## UNA VEZ HECHO TODOS LOS CAMBIOS NECESARIOS, ARCHIVOS AGREGADOS, ETC:
- `git add .`: Agrega todos los cambios y modificaciones hechas
- `git commit -m "(mensaje)"`: Para comitear
- `git remote add origin https://github.com/Dario2711/Activate`: Vincula el repo remoto con el local
- `git push origin (nombre-rama)`: Pushea los cambios hecho

## PARA MERGEAR ESTA RAMA CON DEVELOP (UNA VEZ HECHO TODOS LOS CAMBIOS): 
1. Clckear en 'Compare & pull request' `base: develop` <- `compare: (nombre-rama)` 
2. Clickear en 'Create pull request'
3. ESPERAR A QUE SE ACEPTE LA REQUEST / Ir a 'Pull requests' y darle donde dice 'Merge pull request' (Solo si aparece y deja)
4. BORRAR LA RAMA DEL REPO REMOTO: `git push origin --delate (nombre-rama)` / Darle a donde dice 'Delete branch'
5. BORRAR LA RAMA DEL REPO LOCAL: `git branch -D (nombre-rama)`
- **La rama se borra SOLAMENTE cuando ya fue mergeada a develop (o a su sub rama)**
