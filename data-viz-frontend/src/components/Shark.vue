<template>
    <div>
        <button type="button" class = "btn btn-primary">{{ msg }}</button>
    </div>
</template>


<script>
//import { ref } from 'vue';
import axios from 'axios'
export default {
    
    name:'Shark',
    data() {
        return {
            msg : "click"
        };
    },
    methods : {
        getReponse(){
            const path = 'http://localhost:5000/shark'
            axios.get(path)
            .then ((res) => { 
                console.log(res.data)
                
                this.msg = res.data;
            }) 
            .catch ((err) => {
                this.msg = "oopsie, something went wrong"
                console.error(err)
            });
        },
    },
    computed: {
        console: () => console,
        window: () => window,
    },
    created(){
        this.getReponse()
    }
}
</script>