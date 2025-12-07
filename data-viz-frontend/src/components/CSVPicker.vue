<script setup lang="ts">
import { inject, ref } from "vue";
import { EMITTER_KEY } from "../injection-keys";
import { CSV_FILE} from "../emitter-messages";

const emitter = inject(EMITTER_KEY);

let isFileChosen = ref(false);
const chosenFile = ref<string | null>(null);


function storeChosenFile() {
  if (!emitter) throw new Error("Toplevel failed to provide emitter"); // Error checking

//   chosenFile.value = $refs.fileInput.files[0];
  var fileInput = document.getElementById('fileInput') as HTMLInputElement;
  if(fileInput.files) {
    chosenFile.value = fileInput.files[0].name;
    console.log("File chosen: " + chosenFile.value)
    if(chosenFile.value.endsWith('csv')) { 
      isFileChosen.value = true;
      console.log("Sending data thru emitter: " + chosenFile.value);
      emitter.emit(CSV_FILE, {file_name: chosenFile.value});
    } else {
      isFileChosen.value = false;
    }

  }
}

</script>

<template>
  <div id="fileChooser">
<!-- <input type="file" ref="fileInput" @change="handleFileChange()" /> -->
  <input type="file" id="fileInput" />
  <button @click="storeChosenFile">
    <!-- <font-awesome-icon :icon="isFileChosen.value ? 'faFile' : 'faFileUpload'"></font-awesome-icon> -->
    {{ isFileChosen ? 'File Chosen' : 'Confirm File Choice' }}
  </button>
</div>
</template>

<style scoped>

#playback {
  width: 20%;
  display: flex;
  flex-direction: column;
  gap: 20px;
}
</style>
