//! Picking and selection systems.

use bevy::picking::prelude::{Click, Pointer, PointerButton};
use bevy::prelude::*;

use crate::ecs::components::{ElementMarker, Selected, StructuralElement};
use crate::ecs::events::SelectionChangedEvent;
use crate::ecs::resources::{ModelStats, SelectionState, SelectionTypeFilter, ToolMode};

/// Handles element click selection with single, additive, and toggle behavior.
pub fn handle_element_click_selection(
    mut commands: Commands<'_, '_>,
    mut clicks: MessageReader<'_, '_, Pointer<Click>>,
    keys: Res<'_, ButtonInput<KeyCode>>,
    mouse: Res<'_, ButtonInput<MouseButton>>,
    mut selection_state: ResMut<'_, SelectionState>,
    mut model_stats: ResMut<'_, ModelStats>,
    mut changed: MessageWriter<'_, SelectionChangedEvent>,
    tool_mode: Res<'_, ToolMode>,
    type_filter: Res<'_, SelectionTypeFilter>,
    element_query: Query<'_, '_, (Entity, &StructuralElement), With<ElementMarker>>,
    selected_query: Query<'_, '_, Entity, (With<ElementMarker>, With<Selected>)>,
) {
    if *tool_mode != ToolMode::Select {
        return;
    }

    let add_mode = keys.pressed(KeyCode::ShiftLeft) || keys.pressed(KeyCode::ShiftRight);
    let toggle_mode = keys.pressed(KeyCode::ControlLeft) || keys.pressed(KeyCode::ControlRight);

    let mut clicked_target: Option<(Entity, u32)> = None;
    for click in clicks.read() {
        if click.button != PointerButton::Primary {
            continue;
        }
        if let Ok((entity, element)) = element_query.get(click.entity) {
            if !type_filter.allows(&element.element_type) {
                continue;
            }
            clicked_target = Some((entity, element.id));
            break;
        }
    }

    let mut selection_changed = false;
    if let Some((entity, element_id)) = clicked_target {
        if toggle_mode {
            if selection_state.selected_elements.contains(&element_id) {
                commands.entity(entity).remove::<Selected>();
                selection_state
                    .selected_elements
                    .retain(|id| *id != element_id);
            } else {
                commands.entity(entity).insert(Selected);
                selection_state.selected_elements.push(element_id);
            }
            selection_changed = true;
        } else if add_mode {
            if !selection_state.selected_elements.contains(&element_id) {
                commands.entity(entity).insert(Selected);
                selection_state.selected_elements.push(element_id);
                selection_changed = true;
            }
        } else {
            for selected_entity in &selected_query {
                commands.entity(selected_entity).remove::<Selected>();
            }
            commands.entity(entity).insert(Selected);
            selection_state.selected_elements.clear();
            selection_state.selected_elements.push(element_id);
            selection_changed = true;
        }
    } else if mouse.just_pressed(MouseButton::Left) && !add_mode && !toggle_mode {
        if !selection_state.selected_elements.is_empty() {
            for selected_entity in &selected_query {
                commands.entity(selected_entity).remove::<Selected>();
            }
            selection_state.selected_elements.clear();
            selection_changed = true;
        }
    }

    if selection_changed {
        selection_state.selected_nodes.clear();
        model_stats.selected_count = selection_state.selected_elements.len();
        changed.write(SelectionChangedEvent);
    }
}
