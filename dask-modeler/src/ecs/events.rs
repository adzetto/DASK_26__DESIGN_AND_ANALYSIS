//! ECS event declarations.

use bevy::prelude::*;

/// Emitted when selection changes.
#[derive(Message, Clone, Debug, Default)]
pub struct SelectionChangedEvent;
