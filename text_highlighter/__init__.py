import os
import streamlit.components.v1 as components
from typing import List, Dict, Any, Optional, Tuple

# Create a _RELEASE constant. We'll set this to False while we're developing
# the component, and True when we're ready to package and distribute it.
# (This is, of course, optional - there are innumerable ways to manage your
# release process.)
_RELEASE = str(os.environ.get("RELEASE", True)).lower() in ["true", "1"]

# Declare a Streamlit component. `declare_component` returns a function
# that is used to create instances of the component. We're naming this
# function "_component_func", with an underscore prefix, because we don't want
# to expose it directly to users. Instead, we will create a custom wrapper
# function, below, that will serve as our component's public API.

# It's worth noting that this call to `declare_component` is the
# *only thing* you need to do to create the binding between Streamlit and
# your component frontend. Everything else we do in this file is simply a
# best practice.

if not _RELEASE:
    _component_func = components.declare_component(
        # We give the component a simple, descriptive name ("text_highlighter"
        # does not fit this bill, so please choose something better for your
        # own component :)
        "text_highlighter",
        # Pass `url` here to tell Streamlit that the component will be served
        # by the local dev server that you run via `npm run start`.
        # (This is useful while your component is in development.)
        url="http://localhost:3001",
    )
else:
    # When we're distributing a production version of the component, we'll
    # replace the `url` param with `path`, and point it to to the component's
    # build directory:
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "frontend/build")
    _component_func = components.declare_component("text_highlighter", path=build_dir)


# Create a wrapper function for the component. This is an optional
# best practice - we could simply expose the component function returned by
# `declare_component` and call it done. The wrapper allows us to customize
# our component's API: we can pre-process its input args, post-process its
# output value, and add a docstring for users.
def text_highlighter(
    text: str,
    labels: List[Tuple[Any, Any]],
    selected_label: Optional[str] = None,
    annotations: Optional[List[Dict[Any, Any]]] = None,
    key: Optional[str] = None,
    show_label_selector: bool = True,
):
    """A text highlighter component.

    Parameters
    ----------
    text : str
        The text to be annotated
    labels : List[Tuple[Any, Any]]]
        A list of tuples (label, color) (e.g. [("PERSON", "red"), ("ORG", "#0000FF")])
    selected_label : Optional[str]
        The label to highlight (default: this first label)
    annotations : Optional[List[Dict[Any, Any]]]
        The annotations to highlight
    key : Optional[str]
        A unique key to use for the component
    show_label_selector : bool
        Whether to show the label selector

    Examples
    --------
    >>> import streamlit as st
    >>> import text_highlighter
    >>> text = "Hello world!"
    >>> labels = [("PERSON", "red"), ("LOCATION", "#0000FF")]
    >>> annotations = [
    ...     {"start": 7, "end": 11, "label": "LOCATION"},
    ... ]
    >>> text_highlighter.text_highlighter(text, labels, annotations=annotations)
    """
    annotations = [] if annotations is None else annotations
    label_names = [item[0] for item in labels]
    colors = [item[1] for item in labels]
    annotations = [
        {**annotation, "color": colors[label_names.index(annotation["tag"])]}
        for annotation in annotations
    ]
    selected_label = label_names[0] if selected_label is None else selected_label
    # Call through to our private component function. Arguments we pass here
    # will be sent to the frontend, where they'll be available in an "args"
    # dictionary.
    #
    # "default" is a special argument that specifies the initial return
    # value of the component before the user has interacted with it.
    component_value = _component_func(
        text=text,
        annotations=annotations,
        colors=colors,
        labels=label_names,
        key=key,
        default=annotations,
        selected_label=selected_label,
        show_label_selector=show_label_selector,
    )

    class ComponentResult(list):  # type: ignore
        def __init__(self, component_value: List[Dict[Any, Any]], text: str):
            super().__init__(component_value)
            self.text = text

        def _get_start_position(self, annotation: Dict[Any, Any]):
            return annotation["start"]

        def to_xml(self):
            # Generate XML from the annotations
            # which will add tags to the text
            # First, partition the text into chunks; either annotated or not
            chunks = []
            start = 0
            sorted_annotations = sorted(self, key=self._get_start_position)
            for annotation in sorted_annotations:
                if annotation["start"] > start:
                    chunks.append({"text": text[start : annotation["start"]]})
                chunks.append(
                    {
                        "text": text[annotation["start"] : annotation["end"]],
                        "tag": annotation["tag"],
                    }
                )
                start = annotation["end"]
            if start < len(text):
                chunks.append({"text": text[start:]})
            xml = (
                """<?xml version="1.0" encoding="UTF-8"?>\n"""
                + "  <text>\n"
                + "    "
                + "".join(
                    [
                        f"<annotation tag=\"{chunk['tag']}\">{chunk['text']}</annotation>"
                        if "tag" in chunk
                        else chunk["text"]
                        for chunk in chunks
                    ]
                )
                + "\n"
                + "  </text>"
            )
            return xml

    # We could modify the value returned from the component if we wanted.
    # There's no need to do this in our simple example - but it's an option.
    return ComponentResult(component_value, text)


# Add some test code to play with the component while it's in development.
# During development, we can run this just as we would any other Streamlit
# app: `$ streamlit run text_highlighter/__init__.py`
if not _RELEASE:
    import streamlit as st

    st.subheader("Component with constant args")

    component = text_highlighter(
        text="John Doe is the founder of MyComp Inc. and lives in New York with his wife Jane Doe.",
        annotations=[
            {"start": 0, "end": 8, "tag": "PERSON"},
            {"start": 27, "end": 38, "tag": "ORG"},
            {"start": 75, "end": 83, "tag": "PERSON"},
        ],
        labels=[("PERSON", "red"), ("ORG", "#0000FF")],
        selected_label="ORG",
    )
    st.code(component.to_xml())
    st.write(component)
