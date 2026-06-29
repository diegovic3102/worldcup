<template>

    <div class="ecuador-box" v-if="loaded">

        <div v-if="!partido.activo">
            <h3>🇪🇨 Fases finales Ecuador</h3>
            <p>
                Esperando definición del partido...
            </p>
        </div>


        <div v-else>

            <div class="section-heading">
                <div>
                    <p>APUESTA</p>
                    <h2>{{ partido.fase }}</h2>
                </div>
            </div>


            <div class="match">

                <div class="team">
                    <strong>
                        {{ partido.local.nombre }}
                    </strong>

                    <input type="number" v-model="marcador.local" min="0" :readonly="locked" />
                </div>


                <span>
                    VS
                </span>


                <div class="team">

                    <strong>
                        {{ partido.visitante.nombre }}
                    </strong>

                    <input type="number" v-model="marcador.visitante" min="0" :readonly="locked" />

                </div>

            </div>


            <button v-if="!locked && marcador.local === null" class="btn-save" @click="guardar">

                Guardar marcador

            </button>


            <p v-else class="locked-msg">
                ✅ Marcador registrado y bloqueado
            </p>


        </div>

    </div>

</template>



<script lang="ts">

import { defineComponent } from 'vue'


const API_BASE_URL = '/worldcup/api'


export default defineComponent({

    name: 'ApuestasEcuadorFases',


    props: {
        currentUser: {
            type: Object,
            required: true
        }
    },


    data() {

        return {

            partido: {
                activo: false
            } as any,


            marcador: {
                local: null,
                visitante: null
            },

            locked: false,

            loaded: false

        }

    },



    mounted() {

        this.esperarUsuario()

    },



    methods: {

        async esperarUsuario() {

            let intentos = 0

            while (!this.currentUser?.id && intentos < 20) {

                await new Promise(resolve => setTimeout(resolve, 300))

                intentos++

            }


            this.cargar()

        },


        async cargar() {


            const res = await fetch(
                `${API_BASE_URL}/apuestas/ecuador-fase`
            )


            const data = await res.json()


            this.partido = data


            if (!this.currentUser?.id || !data.id) {
                return
            }


            const pred = await fetch(
                `${API_BASE_URL}/apuestas/ecuador-fase/me?usuarioId=${this.currentUser.id}&partidoId=${data.id}`
            )


            const predData = await pred.json()


            console.log("Mi predicción:", predData)


            if (predData.guardado === true) {

                this.marcador.local = predData.goles_local
                this.marcador.visitante = predData.goles_visitante

                this.locked = true

            }


            this.loaded = true

        },



        async guardar() {


            const res = await fetch(
                `${API_BASE_URL}/apuestas/ecuador-fase`,
                {
                    method: 'POST',

                    headers: {
                        'Content-Type': 'application/json'
                    },


                    body: JSON.stringify({

                        usuario_id: this.currentUser.id,

                        partido_id: this.partido.id,

                        goles_local: this.marcador.local,

                        goles_visitante: this.marcador.visitante

                    })

                })


            const data = await res.json()


            if (res.status === 403) {

                alert(data.message)

                this.locked = true

                return
            }


            this.locked = true


            alert('Marcador guardado')


        }


    }



})


</script>



<style scoped>
.locked-msg {

    margin-top: 15px;
    color: #0f766e;
    font-weight: 800;

}

.ecuador-box {

    margin-top: 25px;
    background: white;
    padding: 20px;
    border-radius: 12px;
    border: 1px solid #d9e2ec;

}


.match {

    display: flex;
    justify-content: center;
    align-items: center;
    gap: 30px;
    margin: 25px 0;

}


.team {

    display: grid;
    gap: 10px;
    text-align: center;

}


input {

    width: 80px;
    height: 50px;
    font-size: 24px;
    text-align: center;

}


.btn-save {

    background: #0f766e;
    color: white;
    border: none;
    padding: 12px 18px;
    border-radius: 8px;
    font-weight: 800;

}
</style>