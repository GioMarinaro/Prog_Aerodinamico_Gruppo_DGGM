#!/bin/bash

BASE_DIR=$(pwd)

for dir in Be_153_055_*; do
    if [ -d "$dir" ]; then
        echo "📁 Processing $dir..."
        cd "$BASE_DIR/$dir"

        # 1. Genera mesh
        GEO_FILE=$(ls *.geo 2>/dev/null)
        if [ -n "$GEO_FILE" ]; then
            echo "👉 Mesh da $GEO_FILE"
            gmsh -2 "$GEO_FILE" -format su2
            if [ $? -ne 0 ]; then
                echo "❌ Errore durante la mesh. Salto $dir."
                cd "$BASE_DIR"
                continue
            fi
        else
            echo "⚠️ Nessun file .geo trovato. Salto $dir."
            cd "$BASE_DIR"
            continue
        fi

        # 2. Trova file .cfg
        CFG_FILE=$(ls *.cfg 2>/dev/null)
        if [ -z "$CFG_FILE" ]; then
            echo "⚠️ Nessun .cfg trovato. Salto $dir."
            cd "$BASE_DIR"
            continue
        fi

        # 3. Lancia SU2 in parallelo
        echo "🚀 Lancio SU2_CFD su $CFG_FILE"
        mpirun -n 6 SU2_CFD "$CFG_FILE" > output.log 2>&1
        if [ $? -ne 0 ]; then
            echo "❌ Errore durante SU2_CFD. Salto $dir."
            cd "$BASE_DIR"
            continue
        fi

        # 4. Estrai Cl e Cd
        if [ -f "history.csv" ]; then
            last_line=$(tail -n 1 history.csv)
            Cd=$(echo "$last_line" | cut -d ',' -f 24)
            Cl=$(echo "$last_line" | cut -d ',' -f 25)
            echo "Cl = $Cl | Cd = $Cd" > Result.txt
            echo "✅ Risultati salvati in $dir/Result.txt"
        else
            echo "⚠️ history.csv non trovato. Nessun risultato."
        fi

        cd "$BASE_DIR"
        echo "------------------------"
    fi
done

echo "🎉 Tutte le simulazioni sono state processate!"
