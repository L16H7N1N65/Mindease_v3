#!/bin/bash

# List of common ShadCN UI components to add
components=(
  button
  card
  input
  label
  textarea
  tabs
  select
  toggle
  checkbox
  radio
  slider
  avatar
  badge
  breadcrumb
  dialog
  dropdown-menu
  hover-card
  indicator
  menu
  modal
  popover
  progress
  ring
  separator
  toast
  tooltip
)

# Loop through each component and add it via the CLI
for component in "${components[@]}"; do
  echo "Adding component: $component"
  npx shadcn@latest add "$component"
done

echo "All components have been added."
