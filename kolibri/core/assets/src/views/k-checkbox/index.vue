<template>

  <div
    class="k-checkbox-container"
    :class="{ 'k-checkbox-disabled': disabled }"
    @click.prevent="toggleCheck"
  >
    <div class="tr">

      <div class="k-checkbox" :class="{ 'k-checkbox-active': isActive }">
        <input
          ref="kCheckboxInput"
          type="checkbox"
          class="k-checkbox-input"
          :id="id"
          :checked="isCurrentlyChecked"
          :indeterminate.prop="isCurrentlyIndeterminate"
          :disabled="disabled"
          :title="label"
          @click.stop="toggleCheck"
          @focus="isActive = true"
          @blur="isActive = false"
        >

        <mat-svg
          v-if="isCurrentlyIndeterminate"
          category="toggle"
          name="indeterminate_check_box"
          class="k-checkbox-indeterminate"
        />
        <mat-svg
          v-else-if="!isCurrentlyIndeterminate && isCurrentlyChecked"
          category="toggle"
          name="check_box"
          class="k-checkbox-checked"
        />
        <mat-svg
          v-else
          category="toggle"
          name="check_box_outline_blank"
          class="k-checkbox-unchecked"
        />

      </div>

      <label
        v-if="label"
        class="k-checkbox-label"
        :for="id"
        :class="{ 'visuallyhidden': !showLabel }"
      >
        {{ label }}
      </label>

    </div>
  </div>

</template>


<script>

  /**
    * Used for selection
    */
  export default {
    name: 'k-checkbox',
    props: {
      /**
       * Label
       */
      label: {
        type: String,
        required: true,
      },
      /**
       * Whether to show label
       */
      showLabel: {
        type: Boolean,
        default: true,
      },
      /**
       * Checked state
       */
      checked: {
        type: Boolean,
        default: false,
      },
      /**
       * Indeterminate state, overrides checked state
       */
      indeterminate: {
        type: Boolean,
        default: false,
      },
      /**
       * Disabled state
       */
      disabled: {
        type: Boolean,
        default: false,
      },
    },
    data: () => ({
      isCurrentlyChecked: false,
      isCurrentlyIndeterminate: false,
      isActive: false,
    }),
    computed: {
      id() {
        return `k-checkbox-${this._uid}`;
      },
    },
    watch: {
      checked(newCheckedState) {
        this.isCurrentlyChecked = newCheckedState;
      },
      indeterminate(newIndeterminateState) {
        this.isCurrentlyIndeterminate = newIndeterminateState;
      },
    },
    created() {
      this.isCurrentlyChecked = this.checked;
      this.isCurrentlyIndeterminate = this.indeterminate;
    },
    methods: {
      toggleCheck(event) {
        if (!this.disabled) {
          this.isCurrentlyChecked = !this.isCurrentlyChecked;
          this.$refs.kCheckboxInput.focus();
          this.isCurrentlyIndeterminate = false;
          /**
           * Emits change event
           */
          this.$emit('change', this.isCurrentlyChecked, event);
        }
      },
    },
  };

</script>


<style lang="stylus" scoped>

  @require '~kolibri.styles.definitions'

  $checkbox-height = 24px

  .k-checkbox-container
    display: table
    margin-top: 8px
    margin-bottom: 8px

  .tr
    display: table-row

  .k-checkbox
    display: table-cell
    position: relative
    vertical-align: top
    width: $checkbox-height
    height: $checkbox-height
    cursor: pointer

  .k-checkbox-input
    position: absolute
    top: 50%
    left: 50%
    transform: translate(-50%, -50%)
    opacity: 0
    cursor: pointer

  .k-checkbox-checked, .k-checkbox-indeterminate
    fill: $core-action-normal

  .k-checkbox-unchecked
    fill: $core-text-annotation

  .k-checkbox-active
    .k-checkbox-checked, .k-checkbox-indeterminate
      outline: $core-outline

    .k-checkbox-unchecked
      outline: $core-outline

  .k-checkbox-label
    display: table-cell
    padding-left: 8px
    cursor: pointer
    line-height: 24px
    user-select: none

  .k-checkbox-disabled
    svg
      fill: $core-grey-300

    .k-checkbox, .k-checkbox-input, .k-checkbox-label
      cursor: default

    .k-checkbox-label
      color: $core-text-disabled

</style>
