[**flashoffer-react**](../README.md)

***

# Interface: EngagementContextValue

Defined in: src/analytics/EngagementProvider.tsx:46

## Properties

### register()

> **register**: (`trackId`, `element`, `meta?`) => () => `void`

Defined in: src/analytics/EngagementProvider.tsx:47

#### Parameters

##### trackId

`string`

##### element

`null` | `Element`

##### meta?

`Record`\<`string`, `unknown`\>

#### Returns

> (): `void`

##### Returns

`void`

***

### attachElement()

> **attachElement**: (`trackId`, `element`, `meta?`) => () => `void`

Defined in: src/analytics/EngagementProvider.tsx:52

#### Parameters

##### trackId

`string`

##### element

`null` | `Element`

##### meta?

`Record`\<`string`, `unknown`\>

#### Returns

> (): `void`

##### Returns

`void`

***

### detachElement()

> **detachElement**: (`element`) => `void`

Defined in: src/analytics/EngagementProvider.tsx:57

#### Parameters

##### element

`null` | `Element`

#### Returns

`void`

***

### recordInteraction()

> **recordInteraction**: (`target`, `meta?`) => `void`

Defined in: src/analytics/EngagementProvider.tsx:58

#### Parameters

##### target

`string`

##### meta?

`Record`\<`string`, `unknown`\>

#### Returns

`void`

***

### getActiveTargets()

> **getActiveTargets**: () => `string`[]

Defined in: src/analytics/EngagementProvider.tsx:59

#### Returns

`string`[]
