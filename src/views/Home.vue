<template>
  <v-container>
    <v-row>
      <v-col>
        <div class="text-h6 font-weight-regular mb-4 text-medium-emphasis pl-4 no-print">Please enter case details below, then submit:</div>
        
        <v-card class="mb-6 pa-4" elevation="2">
          <v-card-text>
            <v-form
              ref="form"
              @submit.prevent="handleSubmit"
              v-model="formValid"
              class="no-print"
            >
              <!-- Row for ID and DOS -->
              <v-row justify="center">
                <v-col cols="12" sm="10" md="5">
                  <v-text-field
                    v-model="formData.ID"
                    label="Patient ID"
                    variant="outlined"
                    color="primary"
                    density="compact" 
                    :rules="[rules.required]"
                  ></v-text-field>
                </v-col>
                <v-col cols="12" sm="10" md="5">
                  <v-text-field
                    v-model="formData.DOS"
                    label="Date of Surgery"
                    type="date"
                    variant="outlined"
                    color="primary"
                    density="compact" 
                    :rules="[rules.required]"
                  ></v-text-field>
                </v-col>
              </v-row>

              <!-- Row for Age and Eye -->
              <v-row justify="center" class="align-center my-2">
                <v-col cols="12" sm="10" md="5">
                  <v-text-field
                    v-model="formData.age"
                    label="Age (years)"
                    type="number"
                    min="21" 
                    max="120"
                    step="1"
                    variant="outlined"
                    color="primary"
                    density="compact" 
                    :rules="[rules.required, rules.ageRange]"
                  ></v-text-field>
                </v-col>
                <v-col cols="12" sm="10" md="5">
                  <div class="d-flex align-center" style="gap: 16px;">
                    <span class="eye-inline-label text-body-1 text-medium-emphasis ml-4 eye-label-large">Eye</span>
                    <v-radio-group
                      v-model="formData.eye"
                      inline
                      color="primary"
                      class="mb-0 radio-align"
                      :rules="[rules.required]"
                      style="margin-bottom: 0; align-items: center; display: flex; margin-top: -6px;"
                    >
                      <v-radio
                        label="Right"
                        value="OD"
                        class="me-4 text-medium-emphasis"
                      ></v-radio>
                      <v-radio
                        label="Left"
                        value="OS"
                        class="me-4 text-medium-emphasis"
                      ></v-radio>
                    </v-radio-group>
                  </div>
                </v-col>
              </v-row>

              <!-- Row for Corneal Astigmatism and Steep Axis -->
              <v-row justify="center" style="margin-top: -8px;">
                <v-col cols="12" sm="10" md="5">
                  <v-text-field
                    v-model="formData.corneal_astigmatism"
                    label="Corneal Astigmatism (D)"
                    type="number"
                    min="0.25"
                    max="1.50"
                    step="0.01"
                    variant="outlined"
                    color="primary"
                    density="compact"
                    :rules="[rules.required, rules.cornealAstigmatismRange]"
                  ></v-text-field>
                </v-col>
                <v-col cols="12" sm="10" md="5">
                  <v-text-field
                    v-model="formData.steep_axis"
                    label="Steep Axis (°)"
                    type="number"
                    min="0"
                    max="180"
                    step="1"
                    variant="outlined"
                    color="primary" 
                    density="compact" 
                    :rules="[rules.required, rules.steepAxisRange]"
                  ></v-text-field>
                </v-col>
              </v-row>

              <!-- Row for Mean K and WTW -->
              <v-row justify="center">
                <v-col cols="12" sm="10" md="5">
                  <v-text-field
                    v-model="formData.mean_k"
                    label="Average K (D)"
                    type="number"
                    min="30.00"
                    max="50.00"
                    step="0.01"
                    variant="outlined"
                    color="primary" 
                    density="compact" 
                    :rules="[rules.required, rules.meanKRange]"
                  ></v-text-field>
                </v-col>
                <v-col cols="12" sm="10" md="5">
                  <v-text-field
                    v-model="formData.WTW"
                    label="WTW (mm)"
                    type="number"
                    min="10.0"
                    max="15.0"
                    step="0.1"
                    variant="outlined"
                    color="primary" 
                    density="compact" 
                    :rules="[rules.required, rules.wtwRange]"
                  ></v-text-field>
                </v-col>
              </v-row>

              <!-- Submit Button - Centered -->
              <v-row justify="center">
                <v-col cols="auto">
                  <div class="mt-4">
                    <v-btn 
                      type="submit" 
                      color="primary" 
                      size="large"
                      elevation="2"
                      class="px-8"
                      :disabled="!formValid || isLoading"
                      :loading="isLoading"
                    >
                      Submit
                    </v-btn>
                  </div>
                </v-col>
              </v-row>
            </v-form>

            <v-fade-transition>
              <v-alert
                v-if="showToricAlert"
                type="warning"
                variant="tonal"
                class="mt-4 no-print"
                closable
              >
                Large arcuate incisions are not the best option to correct higher levels of corneal astigmatism (>= 1.25 WTR or >= 0.75 ATR). Consider a toric IOL for a stabler or more predictable alternative.
              </v-alert>
            </v-fade-transition>

            <v-fade-transition>
              <v-alert
                v-if="errorMessage"
                type="error"
                variant="tonal"
                class="mt-4 no-print"
                closable
                @click:close="errorMessage = ''"
              >
                {{ errorMessage }}
              </v-alert>
            </v-fade-transition>
            
            <!-- Print-only patient information -->
            <div class="print-only mt-4">
              <h2 class="text-h5 mb-4">Patient Information</h2>
              <table class="patient-info-table">
                <tbody>
                  <tr>
                    <td><strong>Patient ID:</strong></td>
                    <td>{{ formData.ID }}</td>
                    <td><strong>Date of Surgery:</strong></td>
                    <td>{{ formData.DOS }}</td>
                  </tr>
                  <tr>
                    <td><strong>Age:</strong></td>
                    <td>{{ formData.age }} years</td>
                    <td><strong>Eye:</strong></td>
                    <td>{{ formData.eye === 'OD' ? 'Right' : 'Left' }}</td>
                  </tr>
                  <tr>
                    <td><strong>Corneal Astigmatism:</strong></td>
                    <td>{{ formData.corneal_astigmatism }} D</td>
                    <td><strong>Steep Axis:</strong></td>
                    <td>{{ formData.steep_axis }}°</td>
                  </tr>
                  <tr>
                    <td><strong>Average K:</strong></td>
                    <td>{{ formData.mean_k }} D</td>
                    <td><strong>WTW:</strong></td>
                    <td>{{ formData.WTW }} mm</td>
                  </tr>
                </tbody>
              </table>
            </div>

            <v-fade-transition>
              <div v-if="finalData" class="mt-8">
                <v-card
                  class="bg-grey-darken-3 mb-4 print-dark"
                  elevation="3"
                >
                  <v-card-text>
                    <div class="text-h6" :style="{ color: ARCUATE_COLORS.first }">{{ finalData.arcuate1text }}</div>
                    <div v-if="finalData.arcuate2text" class="text-h6" :style="{ color: ARCUATE_COLORS.second }">{{ finalData.arcuate2text }}</div>
                  </v-card-text>
                </v-card>
                
                <v-card
                  class="mb-4"
                  elevation="2"
                  rounded="lg"
                >
                  <canvas ref="myCanvas" width="1024" height="1024"></canvas>
                  <div class="text-center pa-2 eye-label">
                    <span class="text-h4 font-weight-bold">
                      {{ formData.eye === 'OD' ? 'RIGHT EYE' : 'LEFT EYE' }}
                    </span>
                  </div>
                </v-card>
                
                <!-- Print button appears only after calculation -->
                <v-row justify="center">
                  <v-col cols="auto">
                    <v-btn
                      color="primary"
                      size="large"
                      class="mt-4 no-print"
                      prepend-icon="mdi-printer"
                      @click="printResults"
                    >
                      Print Results
                    </v-btn>
                  </v-col>
                </v-row>
              </div>
            </v-fade-transition>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
    <v-row justify="center" class="mt-auto pb-2 no-print">
      <v-col cols="12" class="text-center text-caption text-medium-emphasis">
        © {{ new Date().getFullYear() }} De Rojas AI Calc. All rights reserved.
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick, watch, computed, defineProps } from 'vue'
import leftEyeTemplate from '@/assets/lefteyetemplate.jpg'
import rightEyeTemplate from '@/assets/righteyetemplate.jpg'

const props = defineProps({
  selectedModel: {
    type: String,
    required: true
  }
})

const form = ref(null)
const formValid = ref(false)
const errorMessage = ref('')
const isLoading = ref(false)

const formData = reactive({
  ID: '',
  DOS: '',
  age: null,
  eye: '',
  corneal_astigmatism: null,
  steep_axis: null,
  mean_k: null,
  WTW: null,
})

const finalData = ref(null)
const myCanvas = ref(null)

const ARCUATE_COLORS = {
  first: '#FFFF00',  // Yellow
  second: '#FFA500'  // Orange
}

// Use environment variable for API connection with fallback
const API_URL = ref(import.meta.env.VITE_API_URL || 'http://localhost:8000');

// Function to check if API is available (for user feedback)
const checkApiAvailability = async () => {
  try {
    const response = await fetch(`${API_URL.value}/docs`, { 
      method: 'HEAD',
      mode: 'no-cors' // Just to check if server responds
    });
    return true;
  } catch (error) {
    return false;
  }
};

const rules = {
  required: value => !!value || 'Required field',
  ageRange: value => {
    const num = Number(value)
    return (num >= 21 && num <= 120) || 'Age must be between 21 and 120 years'
  },
  cornealAstigmatismRange: value => {
    const num = Number(value)
    return (num >= 0.25 && num <= 1.50) || 'Corneal Astigmatism must be between 0.25 and 1.50 D'
  },
  steepAxisRange: value => {
    const num = Number(value)
    return (num >= 0 && num <= 180) || 'Steep Axis must be between 0° and 180°'
  },
  meanKRange: value => {
    const num = Number(value)
    return (num >= 30.00 && num <= 50.00) || 'Average K must be between 30.00 and 50.00 D'
  },
  wtwRange: value => {
    const num = Number(value)
    return (num >= 10.0 && num <= 15.0) || 'WTW must be between 10.0 and 15.0 mm'
  }
}

const showToricAlert = computed(() => {
  const astigmatism = Number(formData.corneal_astigmatism)
  return astigmatism >= 0.75
})

// Add watcher for formData changes OR selectedModel prop changes
watch([formData, () => props.selectedModel], () => {
  // Only clear if we already have results showing
  if (finalData.value) {
    finalData.value = null
  }
}, { deep: true })

const drawArcuates = () => {
  if (!myCanvas.value || !finalData.value || !formData.eye) return

  const ctx = myCanvas.value.getContext('2d')
  if (!ctx) return

  const img = new Image()
  img.src = formData.eye === 'OD' ? rightEyeTemplate : leftEyeTemplate

  img.onload = () => {
    // Clear canvas
    ctx.clearRect(0, 0, myCanvas.value.width, myCanvas.value.height)
    
    // Draw background image
    ctx.drawImage(img, 0, 0, myCanvas.value.width, myCanvas.value.height)

    // Check if incisions are needed before drawing arcs
    if (finalData.value.arcuate1text === "No arcuate incision needed") {
      return; // Don't draw arcs if none are needed
    }

    // Draw arcuates
    const radius = 360// Adjusted for 1024x1024 images
    const center = { x: 512, y: 512 } // Center of 1024x1024 image for both eyes

    // Draw first arcuate
    ctx.beginPath()
    ctx.arc(center.x, center.y, radius, finalData.value.arc1start, finalData.value.arc1end)
    ctx.strokeStyle = ARCUATE_COLORS.first
    ctx.lineWidth = 10
    ctx.stroke()

    // Draw second arcuate if it exists (paired arcuates)
    if (finalData.value.arcuate2text) {
      ctx.beginPath()
      ctx.arc(center.x, center.y, radius, finalData.value.arc2start, finalData.value.arc2end)
      ctx.strokeStyle = ARCUATE_COLORS.second
      ctx.lineWidth = 10
      ctx.stroke()
    }
  }
}

const printResults = () => {
  window.print()
}

const handleSubmit = async () => {
  const { valid } = await form.value.validate()
  
  if (!valid) {
    return
  }

  try {
    // Show loading state
    isLoading.value = true;
    errorMessage.value = '';
    
    // Check API availability
    const apiAvailable = await checkApiAvailability();
    if (!apiAvailable) {
      throw new Error('API not available. Please try again later.');
    }
    
    // Prepare data with correct types
    const dataToSend = {
      ID: formData.ID,
      DOS: formData.DOS,
      age: parseInt(formData.age),
      eye: formData.eye,
      corneal_astigmatism: parseFloat(formData.corneal_astigmatism),
      steep_axis: parseFloat(formData.steep_axis),
      mean_k: parseFloat(formData.mean_k),
      WTW: parseFloat(formData.WTW),
      model_choice: props.selectedModel
    };
    
    console.log(`Sending request to ${API_URL.value}/predict with data:`, dataToSend);
    
    const response = await fetch(`${API_URL.value}/predict`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      credentials: 'omit', // Don't send credentials for cross-origin requests
      body: JSON.stringify(dataToSend)
    });

    if (!response.ok) {
      let errorText = `HTTP error! Status: ${response.status}`;
      try {
        const errorData = await response.json();
        errorText = errorData.detail || errorText;
      } catch (e) {
        // If JSON parsing fails, use the status text
        errorText = `Error ${response.status}: ${response.statusText}`;
      }
      throw new Error(errorText);
    }

    const fetchedData = await response.json();
    finalData.value = fetchedData;
    await nextTick();
    drawArcuates();
  } catch (error) {
    console.error('Error during prediction:', error);
    errorMessage.value = error.message || 'Error calculating arcuates. Please try again.';
    finalData.value = null; // Clear any previous results
  } finally {
    // Hide loading state when done (success or error)
    isLoading.value = false;
  }
}

// Try to find working API port on component mount
onMounted(async () => {
  // Preload images
  const rightImg = new Image()
  const leftImg = new Image()
  
  rightImg.src = rightEyeTemplate
  leftImg.src = leftEyeTemplate
  
  // Check API availability
  try {
    const apiAvailable = await checkApiAvailability();
    if (apiAvailable) {
      console.log(`Backend API available at ${API_URL.value}`);
    }
  } catch (error) {
    console.error('Error checking API availability:', error);
  }
});
</script>

<style scoped>
/* Custom styles for input-field and border-radius removed */

.v-text-field :deep(.v-field__outline__start) {
  /* border-radius: 4px 0 0 4px; */ /* Removed */
}

.v-text-field :deep(.v-field__outline__end) {
  /* border-radius: 0 4px 4px 0; */ /* Removed */
}

.canvas-container {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 16px;
}

canvas {
  width: 100%;
  height: auto;
  background-color: white;
  display: block;
  margin: 0 auto;
  border-radius: 16px;
}

/* Add styling for the eye label */
.eye-label {
  margin-top: 8px;
  background-color: #f5f5f5;
  border-top: 1px solid #e0e0e0;
}

/* Print-specific styles */
@media print {
  .no-print {
    display: none !important;
  }
  
  .print-only {
    display: block !important;
  }
  
  /* Fixed page size to prevent unnecessary page breaks */
  @page {
    size: auto;
    margin: 10mm;
  }
  
  .v-container {
    padding: 0 !important;
    margin: 0 !important;
    width: 100% !important;
    max-width: 100% !important;
  }
  
  .v-card {
    box-shadow: none !important;
    border: 1px solid #eee;
    margin-bottom: 15px !important;
    padding: 0 !important;
    border-radius: 16px !important;
    overflow: hidden !important;
  }
  
  .print-dark {
    background-color: #333 !important;
    color: white !important;
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
  }
  
  canvas {
    max-width: 65% !important; /* Smaller to fit on one page */
    height: auto !important;
    max-height: 325px !important; /* Smaller max height */
    width: auto !important;
    margin: 0 auto;
    page-break-inside: avoid;
    display: block;
    border-radius: 16px !important;
    overflow: hidden !important;
  }
  
  /* Other print optimizations */
  body {
    margin: 0;
    padding: 0;
    background-color: white;
  }
  
  .text-h4 {
    font-size: 22px !important; /* Slightly smaller title */
    margin-bottom: 8px !important;
  }
  
  .eye-label {
    margin-top: 4px !important;
    padding: 6px 0 !important; /* Smaller padding */
    background-color: #f0f0f0 !important;
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
  }
  
  .eye-label span {
    font-size: 22px !important; /* Slightly smaller */
    font-weight: bold !important;
    letter-spacing: 1px;
  }
  
  /* Prevent page breaks */
  .v-application__wrap,
  .v-main,
  .v-main__wrap {
    height: auto !important;
    overflow: visible !important;
    page-break-after: avoid !important;
    page-break-before: avoid !important;
  }
  
  /* Footer fix to prevent page breaks */
  .mt-auto {
    display: none !important;
  }
}

/* Always hide initially */
.print-only {
  display: none;
}

/* Patient information table for print view */
.patient-info-table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 15px;
}

.patient-info-table td {
  padding: 5px 10px;
}

.patient-info-table tr:nth-child(even) {
  background-color: #f5f5f5;
}

.eye-inline-label {
  min-width: 48px;
  display: flex;
  align-items: flex-end;
  height: 40px;
  margin-top: -32px;
  font-size: 18px;
}

.radio-align {
  margin-top: -18px !important;
}

.eye-label-large {
  font-size: 1.15rem !important;
}
</style> 