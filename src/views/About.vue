<template>
  <v-container>
    <v-row>
      <v-col>
        <div class="text-h3 font-weight-medium mb-6">About De Rojas AI Calc</div>

        <div class="text-h5 font-weight-medium mb-3">Background</div>
        <div class="text-body-1 mb-4">Arcuate keratotomies of the cornea (also known as arcuate incisions) are used in ophthalmic surgery to treat astigmatism during cataract surgery and lens exchange procedures. They are a powerful tool, but there is limited medical consensus on how to best employ them, how to create them (e.g., via femtosecond laser or manual blades?), or how to fine-tune them for specific levels of astigmatism or patient characteristics.</div>
        <div class="text-body-1 mb-4">The author, Joaquin De Rojas, MD, has extensive experience using femtosceondlaser arcuate keratotomies to improve visual outcomes for his patients.</div>

        <div class="text-body-1 mb-4">Multiple published models or "nomograms" exist to help guide surgeons on incision parameters (length, distance from center, depth). Links to some prior published nomograms are available in the "Other Resources" menu at the top of the webpage.</div>

        <div class="text-h5 font-weight-medium mb-3 mt-5">The Model</div>
        <div class="text-body-1 mb-4">The De Rojas AI Calc model has been developed using advanced machine learning algorithms and has been trained and validated internally on hundreds of cases (Outcome data obatined from: Joaquin De Rojas, Denise Visco, Priya Mathews, William Soscia). Please note that the model is currently in its BETA version.</div>
        
        <div class="text-h5 font-weight-medium mb-3 mt-5">Model Assumptions</div>
        <div class="text-body-1 mb-4">The model has been trained based on the following assumptions:</div>
        <div class="text-body-1 mb-4">
          <ul class="pl-4">
            <li v-for="(item, i) in assumptions" :key="i" class="mb-2">
              {{ item }}
            </li>
          </ul>
        </div>

        <div class="text-h5 font-weight-medium mb-3 mt-5">Future Development</div>
        <div class="text-body-1 mb-4">The author plans to create updated, customizable versions of this model. Future iterations may allow retraining based on user-submitted datasets with post-operative outcomes.</div>

        <div class="text-h5 font-weight-medium mb-3 mt-5">Disclaimer</div>
        <v-alert
          type="warning"
          class="mb-4 font-weight-bold"
          elevation="2"
          border="start"
          border-color="warning"
        >
          IN ITS CURRENT FORM, THIS WEBSITE/NOMOGRAM IS INTENDED FOR INVESTIGATIONAL PURPOSES ONLY. IT IS NOT APPROVED FOR PATIENT USE OR TO GUIDE SURGICAL CORRECTION OF ASTIGMATISM IN HUMANS OR ANIMALS.
        </v-alert>

        <div class="text-h5 font-weight-medium mb-3 mt-5">Contact</div>
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
  'The ALLY® Robotic Cataract Laser System (LENSAR, Inc) is used to make laser arcuate keratotomies (AKs).',
  'AKs are made at 80% depth.',
  'AKs are made at 4.5mm radius from the visual center.',
  'All AKs were opened at the time of surgery with a BSS irrigation cannula.',
  'We do not recommend treating very low levels of astigmatism (<= 0.2 D) with AKs.',
  'Maximum AK sweep have been capped at 50 degrees. It is our opinion that higher levels of astigmatism should be treated with toric lenses over laser AKs.',
  'The nomogram assumes a clear corneal temporal incision with a 2.4-2.8mm blade which can be assumed to create ~0.2 D of SIA at 180 deg. During training, the model has baked in an internal "average" SIA internally. Inputting a presumed SIA for an individual surgeons has not been shown to significantly improve results.',
  'The current iteration of this model was been trained using K readings and other measurements from the IOLMaster 700 (Zeiss Meditec).'
]
</script>

<style scoped>

</style>