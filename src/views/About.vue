<template>
  <v-container>
    <v-row>
      <v-col>
        <div class="text-h3 font-weight-medium mb-4">About De Rojas AI Calc</div>

        <div class="text-body-1 mb-4">Arcuate incisions of the cornea (aka arcuate keratotomies) are used in ophthalmic surgery to treat astigmatism during cataract surgery 
          and lens exchange procedures. They are a powerful tool, but there is little medical consensus on how to
          best employ them, how to create them (via a femtosecond laser? manual blades?), or how to fine-tune them
          for specific levels of astigmatism and/or patient biometrics or demographics. The author Joaquin De Rojas, MD 
          has extensive experience in employing these laser arcuate incisions/keratotomies to improve visual outcomes for his patients</div>

        <div class="text-body-1 mb-4">There have been multiple published models or "nomograms" to help guide surgeons in how to best make these
          incisions (i.e. how long do you make them? how far from the center of the cornea? How deep?) There are links to these 
          prior published nomograms in the navigation bar "Other Resources" at the top of the webage.</div>

        <div class="text-body-1 mb-4">The current model continues to be developed using advanced machine learing algorithms
          and is still in BETA. The model has been trained on the following assumptions:</div>
        
        <div class="text-body-1 mb-4">
          <ul class="pl-4">
            <li v-for="(item, i) in assumptions" :key="i" class="mb-2">
              {{ item }}
            </li>
          </ul>
        </div>

        <div class="text-body-1 mb-4">The hope of the author is to create updated versions of this model that are customizable.  
          In other words, the underlying model will be retrained once a user submits a dataset with post-op outcomes.</div>

        <v-alert
          type="warning"
          class="mb-4 font-weight-bold"
          elevation="2"
        >
          DISCLAIMER: IN IT'S CURRENT FORM, THIS WEBSITE/NOMOGRAM IS ONLY INTENDED FOR EDUCATIONAL PURPOSES ONLY
          IT IS NOT INTENDED FOR REAL PATIENT USE OR TO GUIDE SURGICAL CORRECTION OF ASTIGMATISM IN HUMANS OR ANIMALS.
        </v-alert>

        <div class="text-body-1 d-flex align-center">
          Please feel free to email the author with any questions or concerns: 
          <v-btn
            href="mailto:joaquin.derojas@gmail.com"
            variant="text"
            class="text-primary pa-0 text-decoration-underline text-none ms-1"
            style="height: auto;"
          >
            joaquin.derojas@gmail.com
          </v-btn>
        </div>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
const assumptions = [
  'The ALLY® Adaptive Cataract Treatment System (LensAR, Inc) is used to make laser arcuate incisions',
  'Arcuate incisions are made at 80% depth',
  'Arcuate incisions are made at 4.5mm radius from the visual center',
  'All arcuate incisions were opened at the time of surgery with a BSS irrigation cannula',
  'We do not recommend treating very low levels of astigmatism (<= 0.2) with laser arcuates where your SIA may have a larger effect than any arcuate. It is our opinion that high levels of astigmatism (>1.50) should also NOT be treated with arcuates since, in such cases, toric lenses can offer a safer and more reliable alternative',
  'Surgically induced astigmatism (SIA) from the surgeon\'s main temporal incision is factored in (incisions were made at 180 degrees with a 2.75mm blade',
  'The first iteration of this model has been trained using measurements from the IOLMaster700 (Zeiss Meditech)'
]
</script>

<style scoped>
/* Removed custom styles as we're now using Vuetify's built-in classes */
</style>