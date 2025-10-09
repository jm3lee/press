[**flashoffer-react**](../README.md)

***

# Interface: FigureProps

Defined in: src/components/Figure.tsx:6

## Properties

### src

> **src**: `string`

Defined in: src/components/Figure.tsx:8

Image source rendered inside the figure.

***

### alt?

> `optional` **alt**: `string`

Defined in: src/components/Figure.tsx:10

Descriptive alt text for the image. Defaults to decorative.

***

### caption?

> `optional` **caption**: `ReactNode`

Defined in: src/components/Figure.tsx:12

Optional caption content rendered below the image.

***

### sx?

> `optional` **sx**: `SxProps`\<`Theme`\>

Defined in: src/components/Figure.tsx:14

Custom styles merged into the root figure element.

***

### imgProps?

> `optional` **imgProps**: `Omit`\<`ImgHTMLAttributes`\<`HTMLImageElement`\>, `"alt"` \| `"src"`\>

Defined in: src/components/Figure.tsx:16

Additional props forwarded to the underlying <img> element.
