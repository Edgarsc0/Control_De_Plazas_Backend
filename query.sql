WITH RECURSIVE CadenaDependencias AS (
    SELECT 
        `Posición` AS Posicion,
        `Nombres` AS Empleado,
        `DependenciaDirecta` AS Jefe_Directo,
        1 AS Nivel_Jerarquico,
        CAST(`Posición` AS CHAR(1000)) AS Ruta_Posiciones,
        CAST(`Nombres` AS CHAR(1000)) AS Ruta_Nombres
    FROM EMPLEADOS_COMPLETOS_SIG
    WHERE `Posición` = '20235242'

    UNION ALL

    SELECT 
        e.`Posición`,
        e.`Nombres`,
        e.`DependenciaDirecta`,
        c.Nivel_Jerarquico + 1,
        CONCAT(c.Ruta_Posiciones, ' -> ', e.`Posición`),
        CONCAT(c.Ruta_Nombres, ' -> ', e.`Nombres`)
    FROM EMPLEADOS_COMPLETOS_SIG e
    INNER JOIN CadenaDependencias c ON e.`DependenciaDirecta` = c.Posicion
    WHERE e.`Posición` IS NOT NULL AND e.`Posición` != ''
)
SELECT * FROM CadenaDependencias ORDER BY Ruta_Posiciones;
