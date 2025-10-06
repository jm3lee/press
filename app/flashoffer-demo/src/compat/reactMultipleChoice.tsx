import Radio from "@mui/material/Radio";
import type { CSSProperties, ReactNode } from "react";
import LegacyOption from "react-multiple-choice/dist/Option";
import {
  Question as LegacyQuestion,
  QuestionGroup as LegacyQuestionGroup,
  Test as LegacyTest
} from "react-multiple-choice";

interface OptionStyleOverrides {
  icon?: CSSProperties;
  option?: CSSProperties;
}

interface PatchedOptionProps {
  value: string;
  children?: ReactNode;
  style?: OptionStyleOverrides;
  selectedStyle?: Pick<OptionStyleOverrides, "option">;
  _isSelected?: boolean;
  _onSelect?: (value: string) => void;
}

interface PatchedOptionInstance {
  props: PatchedOptionProps;
  _patchedInputId?: string;
}

const BASE_OPTION_STYLE: CSSProperties = {
  alignItems: "center",
  borderRadius: 12,
  cursor: "pointer",
  display: "flex",
  gap: 12,
  margin: "5px 0",
  padding: "8px 12px",
  transition: "border-color 0.2s ease, box-shadow 0.2s ease"
};

let optionIdCounter = 0;

const optionPrototype = LegacyOption.prototype as PatchedOptionInstance & {
  render?: () => ReactNode;
  __patched?: boolean;
};

if (!optionPrototype.__patched) {
  optionPrototype.render = function renderOption() {
    const { value, children, style, selectedStyle, _isSelected, _onSelect } =
      this.props;

    if (!this._patchedInputId) {
      optionIdCounter += 1;
      this._patchedInputId = `react-multiple-choice-option-${optionIdCounter}`;
    }

    const computedStyle: CSSProperties = {
      ...BASE_OPTION_STYLE,
      ...(style?.option ?? {})
    };

    if (_isSelected) {
      Object.assign(computedStyle, selectedStyle?.option ?? {});
    }

    const ariaLabel =
      typeof children === "string" || typeof children === "number"
        ? String(children)
        : undefined;

    return (
      <label htmlFor={this._patchedInputId} style={computedStyle}>
        <Radio
          id={this._patchedInputId}
          checked={Boolean(_isSelected)}
          onChange={() => {
            _onSelect?.(value);
          }}
          value={value}
          style={style?.icon}
          inputProps={{ "aria-label": ariaLabel }}
        />
        <span>{children}</span>
      </label>
    );
  };

  optionPrototype.__patched = true;
}

export const Option = LegacyOption;
export const Test = LegacyTest;
export const QuestionGroup = LegacyQuestionGroup;
export const Question = LegacyQuestion;
