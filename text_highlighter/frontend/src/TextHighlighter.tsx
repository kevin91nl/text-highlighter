import {
  Streamlit,
  StreamlitComponentBase,
  withStreamlitConnection,
} from "streamlit-component-lib"
import React, { ReactNode } from "react"
import { TextAnnotator } from 'react-text-annotate'
import { State } from 'react-powerplug'

interface BaseState {
  isFocused: boolean,
  tag: string,
}

/**
 * This is a React-based component template. The `render()` function is called
 * automatically when your component should be re-rendered.
 */
class MyComponent extends StreamlitComponentBase<BaseState> {
  public state = { tag: '', isFocused: false }

  public render = (): ReactNode => {
    // Arguments that are passed to the plugin in Python are accessible
    // via `this.props.args`. Here, we access the "name" arg.
    const annotations = this.props.args["annotations"]
    const colors = this.props.args["colors"]
    const labels = this.props.args["labels"]
    const text = this.props.args["text"]
    const selected_label = this.props.args["selected_label"]
    const show_label_selector = this.props.args["show_label_selector"]

    // Streamlit sends us a theme object via props that we can use to ensure
    // that our component has visuals that match the active theme in a
    // streamlit app.
    const { theme } = this.props
    const style: React.CSSProperties = {}

    // Maintain compatibility with older versions of Streamlit that don't send
    // a theme object.
    if (theme) {
      // Use the theme object to style our button border. Alternatively, the
      // theme style is defined in CSS vars.
      const borderStyling = `1px solid ${this.state.isFocused ? theme.primaryColor : "gray"
        }`
      style.border = borderStyling
      style.outline = borderStyling
    }

    // Show a button and some text.
    // When the button is clicked, we'll increment our "numClicks" state
    // variable, and send its new value back to Streamlit, where it'll
    // be available to the Python program.
    // initial={{ value: [{ start: 18, end: 28, tag: 'PERSON' }], tag: 'PERSON' }}
    return (
      <State initial={{ value: annotations, tag: selected_label }}>
        {({ state, setState }) => (
          <span>
            {show_label_selector && <select
              onChange={e => setState({ tag: e.target.value })}
              value={state.tag}
            >
              {labels.map((label: any) => (
                <option key={label} value={label}>
                  {label}
                </option>
              ))}
            </select>}
            <TextAnnotator
              style={{
                maxWidth: 500,
                lineHeight: 1.5
              }}
              content={text}
              value={state.value}
              onChange={(value: any) => this.updateState(value, setState)}
              getSpan={span => ({
                ...span,
                tag: state.tag,
                color: colors[labels.indexOf(state.tag)],
              })}
            />
          </span>
        )}
      </State>

    )
  }

  private mergeAnnotations = (annotations: any[]) => {
    // Remove all annotations which are a subannotation of another annotation;
    // which means that annotation2.start >= annotation1.start and annotation2.end <= annotation1.end
    for (const annotation1 of annotations) {
      var isOverlapping = false;
      let otherAnnotation = null;
      for (const annotation2 of annotations) {
        if (annotation1.start === annotation2.start && annotation1.end === annotation2.end) continue;
        if ((annotation2.start <= annotation1.start && annotation2.end >= annotation1.start) || (annotation2.start <= annotation1.end && annotation2.end >= annotation1.end)) {
          isOverlapping = true;
          otherAnnotation = annotation2;
          break;
        }
      }
      if (isOverlapping) {
        const newAnnotations = [];
        for (const annotation3 of annotations) {
          if (annotation3.start !== annotation1.start && annotation3.end !== annotation1.end && annotation3.start !== otherAnnotation.start && annotation3.end !== otherAnnotation.end) {
            newAnnotations.push(annotation3);
          }
        }
        // Deselect both annotation1 and otherannotation
        return newAnnotations;
      }
    }
    return annotations;
  }

  private updateState = (value: any, callback: any): void => {
    value = this.mergeAnnotations(value);
    callback({ value });
    Streamlit.setComponentValue(value);
  }

  /** Focus handler for our "Click Me!" button. */
  private _onFocus = (): void => {
    this.setState({ isFocused: true })
  }

  /** Blur handler for our "Click Me!" button. */
  private _onBlur = (): void => {
    this.setState({ isFocused: false })
  }
}

// "withStreamlitConnection" is a wrapper function. It bootstraps the
// connection between your component and the Streamlit app, and handles
// passing arguments from Python -> Component.
//
// You don't need to edit withStreamlitConnection (but you're welcome to!).
export default withStreamlitConnection(MyComponent)
