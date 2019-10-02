if(typeof estnltk === 'undefined'){
  estnltk = {}
}
if(typeof estnltk['syntax_editor' === 'undefined']){
  estnltk['syntax_editor'] = {
    root_div: null,
    edit_mode: 'inactive',
    default_active_cell: null
  }
}

estnltk.syntax_editor['selectTableCell'] = function(cell){
  alert(cell);
  cell.style.backgroundColor = 'pink';
  cell.style.color = 'white';
  if(cell.children[0] != null) cell.children[0].focus();
  else cell.focus();
}

estnltk.syntax_editor['deselectTableCell'] = function(cell){
  cell.style.backgroundColor = '';
  cell.style.color = '';
}


/**** Key bindings for syntax editor widget ****/
// https://stackoverflow.com/questions/22817451/use-arrow-keys-to-navigate-an-html-table
estnltk.syntax_editor['onKeyDown'] = function(event){
  const editKeys = new Set([32, 13, 27]);
  const arrowKeys = new Set([38, 40, 37, 39]);
  const editor = estnltk.syntax_editor;

  let active_cell = document.activeElement.parentElement || estnltk.syntax_editor.default_active_cell;

  if(arrowKeys.has(event.keyCode))
  {
    event.preventDefault();
    let idx = active_cell.cellIndex;
    let next_active_cell = null;

    //Up arrow
    if(event.keyCode == '38'){
      let nextrow = active_cell.parentElement.previousElementSibling;
      if (nextrow == null) return;
      next_active_cell = nextrow.cells[idx];
    }
    // Down arrow
    else if (event.keyCode == '40') {
      let nextrow = active_cell.parentElement.nextElementSibling;
      if (nextrow == null) return;
      next_active_cell = nextrow.cells[idx];
    }
    // Left arrow
    else if (event.keyCode == '37') {

      // This does not work
      let index = Array.from(active_cell.parentElement.parentElement.children).indexOf(active_cell.parentElement);
      next_active_cell = active_cell.parentElement.parentElement.parentElement.parentElement.previousElementSibling.firstElementChild.firstElementChild.children.item(index).firstElementChild;
      // Check styles are different compared to up and down arrows
      if(next_active_cell == null) return;
    }
    // Right arrow
    else if (event.keyCode == '39') {
      let index = Array.from(active_cell.parentElement.parentElement.children).indexOf(start.parentElement);
      next_active_cell = active_cell.parentElement.parentElement.parentElement.parentElement.nextElementSibling.firstElementChild.firstElementChild.children.item(index).firstElementChild;
      // Check styles are different compared to up and down arrows
      if(next_active_cell == null) return;
    }

    editor.deselectTableCell(active_cell);
    editor.selectTableCell(next_active_cell);
  }
  else if (editKeys.has(event.keyCode)){
    // really nothing have to be done to get interaction working
  }
}


/**** Initialisation or activation of the syntax editor widget ***/
estnltk.syntax_editor['onFocus'] = function(event){
  estnltk.syntax_editor.root_div = event.target;

  if(estnltk.syntax_editor.edit_mode !== 'inactive') return;

  // Disable Jupyter key bindings when defined
  if(typeof Jupyter !== 'undefined' && typeof Jupyter.keyboard_manager !== 'undefined'){
    Jupyter.keyboard_manager.disable();
  }

  // Restyle div to indicate selection
  estnltk.syntax_editor.edit_mode = 'traversal';
  event.target.style.backgroundColor = 'pink';
  event.target.style.color = 'white';


  alert(estnltk.syntax_editor.edit_mode);
}


/* Deselection is a hard problem in JavaScript

  https://www.blustemy.io/detecting-a-click-outside-an-element-in-javascript/
  https://www.wikitechy.com/tutorials/javascript/how-to-detect-a-click-outside-an-element
  https://www.cssscript.com/detecting-click-outside-dom-element-clicked-outside/
  https://stackoverflow.com/questions/152975/how-do-i-detect-a-click-outside-an-element

  Hopefully we do not have to solve it
*/
estnltk.syntax_editor['onFocusOut'] = function(e){

  // Does not work as dropdowns steal focus from div
  alert(document.activeElement.tagName);

  if(estnltk.syntax_editor.edit_mode === 'inactive') return;

  estnltk.syntax_editor.edit_mode = 'inactive';
  alert(estnltk.syntax_editor.edit_mode);
}


/**** Attach event handlers to the widget div ****/
var x = document.currentScript.parentElement
x.addEventListener('focus', estnltk.syntax_editor.onFocus, false);
x.addEventListener('keydown', estnltk.syntax_editor.onKeyDown, false);
//x.addEventListener('focusout', estnltk.syntax_editor.onFocusOut, false);
